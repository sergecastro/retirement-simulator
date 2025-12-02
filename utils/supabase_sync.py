"""
Supabase Cloud Sync for Family Forecast
=======================================
Handles anonymous vaults and user account vaults.
All data is encrypted BEFORE sending to Supabase.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Tuple
from supabase import create_client, Client

try:
    from utils.password_crypto import (
        generate_vault_id,
        generate_salt,
        encrypt_with_password,
        decrypt_with_password,
        hash_email
    )
except ImportError:
    from password_crypto import (
        generate_vault_id,
        generate_salt,
        encrypt_with_password,
        decrypt_with_password,
        hash_email
    )


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = "https://ebhzvauommuhqlcswdil.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImViaHp2YXVvbW11aHFsY3N3ZGlsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4OTgyMzYsImV4cCI6MjA3OTQ3NDIzNn0.GlP-4cm2Rkknr5xeh5YOK1oTWCHVnfjKZg1euZYoREo"

TRIAL_DAYS = 30


# =============================================================================
# SUPABASE CLIENT
# =============================================================================

def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# =============================================================================
# ANONYMOUS VAULT FUNCTIONS
# =============================================================================

def create_anonymous_vault(password: str, data: dict) -> Tuple[str, str]:
    """
    Create an anonymous vault with encrypted data.

    Args:
        password: User's chosen password
        data: Dictionary of financial data to encrypt

    Returns:
        (vault_id, message) - Vault ID for user to save
    """
    try:
        client = get_supabase_client()

        # Generate vault ID and salt
        vault_id = generate_vault_id()
        salt = generate_salt()

        # Encrypt the data
        json_data = json.dumps(data)
        encrypted_data = encrypt_with_password(json_data, password, salt)

        # Calculate expiration
        expires_at = (datetime.utcnow() + timedelta(days=TRIAL_DAYS)).isoformat()

        # Store in Supabase
        result = client.table('anonymous_vaults').insert({
            'vault_id': vault_id,
            'salt': salt,
            'encrypted_data': encrypted_data,
            'expires_at': expires_at
        }).execute()

        if result.data:
            return vault_id, f"Vault created! Expires in {TRIAL_DAYS} days."
        else:
            return None, "Failed to create vault"

    except Exception as e:
        return None, f"Error creating vault: {str(e)}"


def load_anonymous_vault(vault_id: str, password: str) -> Tuple[Optional[dict], str]:
    """
    Load and decrypt an anonymous vault.

    Args:
        vault_id: The vault ID (e.g., FF-X7K9-M2PL)
        password: User's password

    Returns:
        (data, message) - Decrypted data or None with error message
    """
    try:
        client = get_supabase_client()

        # Find the vault
        result = client.table('anonymous_vaults').select('*').eq('vault_id', vault_id.upper()).execute()

        if not result.data:
            return None, "Vault not found. Check your Vault ID."

        vault = result.data[0]

        # Check expiration
        expires_at = datetime.fromisoformat(vault['expires_at'].replace('Z', '+00:00'))
        if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
            return None, "This vault has expired. Create an account to keep your data."

        # Decrypt
        salt = vault['salt']
        encrypted_data = vault['encrypted_data']

        decrypted_json = decrypt_with_password(encrypted_data, password, salt)
        data = json.loads(decrypted_json)

        # Calculate days remaining
        days_left = (expires_at - datetime.utcnow().replace(tzinfo=expires_at.tzinfo)).days

        return data, f"Vault loaded! {days_left} days remaining in trial."

    except ValueError:
        return None, "Wrong password. Please try again."
    except Exception as e:
        return None, f"Error loading vault: {str(e)}"


def update_anonymous_vault(vault_id: str, password: str, data: dict) -> Tuple[bool, str]:
    """
    Update an existing anonymous vault with new encrypted data.

    Args:
        vault_id: The vault ID
        password: User's password
        data: New data to encrypt and store

    Returns:
        (success, message)
    """
    try:
        client = get_supabase_client()

        # Find the vault to get salt
        result = client.table('anonymous_vaults').select('salt, expires_at').eq('vault_id', vault_id.upper()).execute()

        if not result.data:
            return False, "Vault not found."

        vault = result.data[0]
        salt = vault['salt']

        # Check expiration
        expires_at = datetime.fromisoformat(vault['expires_at'].replace('Z', '+00:00'))
        if datetime.utcnow().replace(tzinfo=expires_at.tzinfo) > expires_at:
            return False, "This vault has expired."

        # Encrypt new data
        json_data = json.dumps(data)
        encrypted_data = encrypt_with_password(json_data, password, salt)

        # Update in Supabase
        update_result = client.table('anonymous_vaults').update({
            'encrypted_data': encrypted_data,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('vault_id', vault_id.upper()).execute()

        if update_result.data:
            return True, "Vault updated successfully!"
        else:
            return False, "Failed to update vault."

    except Exception as e:
        return False, f"Error updating vault: {str(e)}"


# =============================================================================
# USER ACCOUNT FUNCTIONS (Supabase Auth)
# =============================================================================

def create_user_account(email: str, password: str, data: dict) -> Tuple[bool, str]:
    """
    Create a user account with Supabase Auth and store encrypted data.

    Args:
        email: User's email address
        password: User's password (used for both auth AND encryption)
        data: Financial data to encrypt

    Returns:
        (success, message)
    """
    try:
        client = get_supabase_client()

        # Create auth account
        auth_response = client.auth.sign_up({
            'email': email,
            'password': password
        })

        if not auth_response.user:
            return False, "Failed to create account. Email may already be registered."

        user_id = auth_response.user.id

        # Generate salt and encrypt data
        salt = generate_salt()
        json_data = json.dumps(data)
        encrypted_data = encrypt_with_password(json_data, password, salt)

        # Store encrypted data
        result = client.table('user_vaults').insert({
            'user_id': user_id,
            'salt': salt,
            'encrypted_data': encrypted_data
        }).execute()

        if result.data:
            return True, "Account created! Please check your email to verify."
        else:
            return False, "Account created but failed to save data."

    except Exception as e:
        return False, f"Error creating account: {str(e)}"


def sign_in_user(email: str, password: str) -> Tuple[Optional[dict], str]:
    """
    Sign in user and load their encrypted data.

    Args:
        email: User's email
        password: User's password

    Returns:
        (data, message) - Decrypted data or None
    """
    try:
        client = get_supabase_client()

        # Sign in
        auth_response = client.auth.sign_in_with_password({
            'email': email,
            'password': password
        })

        if not auth_response.user:
            return None, "Invalid email or password."

        user_id = auth_response.user.id

        # Get encrypted data
        result = client.table('user_vaults').select('*').eq('user_id', user_id).execute()

        if not result.data:
            return None, "No saved data found for this account."

        vault = result.data[0]
        salt = vault['salt']
        encrypted_data = vault['encrypted_data']

        # Decrypt
        decrypted_json = decrypt_with_password(encrypted_data, password, salt)
        data = json.loads(decrypted_json)

        return data, "Welcome back!"

    except ValueError:
        return None, "Failed to decrypt data. This shouldn't happen - contact support."
    except Exception as e:
        return None, f"Error signing in: {str(e)}"


def update_user_vault(email: str, password: str, data: dict) -> Tuple[bool, str]:
    """
    Update user's encrypted vault after sign in.

    Args:
        email: User's email
        password: User's password
        data: New data to encrypt

    Returns:
        (success, message)
    """
    try:
        client = get_supabase_client()

        # Get current session
        session = client.auth.get_session()
        if not session:
            return False, "Not signed in."

        user_id = session.user.id

        # Get salt
        result = client.table('user_vaults').select('salt').eq('user_id', user_id).execute()

        if not result.data:
            return False, "No vault found."

        salt = result.data[0]['salt']

        # Encrypt and update
        json_data = json.dumps(data)
        encrypted_data = encrypt_with_password(json_data, password, salt)

        update_result = client.table('user_vaults').update({
            'encrypted_data': encrypted_data,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('user_id', user_id).execute()

        if update_result.data:
            return True, "Data saved!"
        else:
            return False, "Failed to save."

    except Exception as e:
        return False, f"Error saving: {str(e)}"


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("Testing supabase_sync module...")
    print(f"Supabase URL: {SUPABASE_URL}")
    print("Testing connection...")

    try:
        client = get_supabase_client()
        print("[OK] Supabase client created successfully!")

        # Test anonymous vault creation
        print("\nTesting anonymous vault...")
        test_data = {"test": "data", "savings": 100000}
        vault_id, msg = create_anonymous_vault("TestPass123", test_data)

        if vault_id:
            print(f"[OK] Created vault: {vault_id}")
            print(f"   Message: {msg}")

            # Test loading
            loaded_data, load_msg = load_anonymous_vault(vault_id, "TestPass123")
            if loaded_data:
                print(f"[OK] Loaded vault successfully!")
                print(f"   Data matches: {loaded_data == test_data}")
            else:
                print(f"[FAIL] Failed to load: {load_msg}")
        else:
            print(f"[FAIL] Failed to create vault: {msg}")

    except Exception as e:
        print(f"[FAIL] Error: {e}")

    print("\nTests complete!")
