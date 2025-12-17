"""
Supabase Cloud Sync for Family Forecast
=======================================
Handles anonymous vaults and user account vaults.
All data is encrypted BEFORE sending to Supabase.

# =============================================================================
# ⚠️⚠️⚠️ CRITICAL WARNING FOR FUTURE DEVELOPERS ⚠️⚠️⚠️
# =============================================================================
#
# THREE SYSTEMS MUST STAY IN PERFECT SYNC - ANY FIELD CHANGE REQUIRES ALL THREE:
#
#   1. LOVABLE INTAKE (React/TypeScript)
#      - File: src/lib/encryption.ts (field names in encrypted data)
#      - File: IntakeReview.tsx, QuickReview.tsx (form fields)
#
#   2. STREAMLIT INTAKE (Python)
#      - File: pages/financial_inputs.py (form fields with input_* keys)
#      - Uses st.session_state keys like input_salary_wages, input_age, etc.
#
#   3. DATA TRANSFORMER (this file)
#      - Function: transform_lovable_to_streamlit() below
#      - Maps Lovable nested format → Streamlit flat format
#
#   4. STREAMLIT ANALYSIS (Python)
#      - File: simulation/simulation_core.py (reads input_* keys)
#      - File: ui/results_page.py (displays input_* values)
#
# WHAT HAPPENS IF YOU FORGET:
#   - Add field in Lovable only → Data lost in Streamlit
#   - Rename field in Streamlit only → Analysis shows zeros
#   - Change transformer only → Lovable data doesn't map correctly
#
# RULE: ONE CHANGE = CHECK ALL FOUR PLACES
#
# =============================================================================
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
# SIGNUP-ONLY FUNCTIONS (No data required - for Welcome page)
# =============================================================================

def signup_user_only(email: str, password: str) -> Tuple[bool, str]:
    """
    Create a Supabase Auth account WITHOUT uploading data.
    User will sync their data on first save.

    Returns: (success, message)
    """
    try:
        client = get_supabase_client()

        # Create auth account
        response = client.auth.sign_up({
            "email": email,
            "password": password
        })

        if response.user:
            return True, f"Account created for {email}! Your data will sync when you save."
        else:
            return False, "Failed to create account. Please try again."

    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return False, "This email is already registered. Try signing in instead."
        return False, f"Error: {error_msg}"


def create_anonymous_vault_empty(password: str) -> Tuple[Optional[str], str]:
    """
    Create an anonymous vault WITHOUT uploading data.
    User will sync their data on first save.

    Returns: (vault_id or None, message)
    """
    try:
        client = get_supabase_client()

        # Generate vault ID and salt using existing functions
        vault_id = generate_vault_id()
        salt = generate_salt()

        # Store empty vault placeholder
        # encrypted_data will be empty string - filled on first save
        from datetime import datetime, timedelta
        expires_at = (datetime.utcnow() + timedelta(days=TRIAL_DAYS)).isoformat()

        result = client.table('anonymous_vaults').insert({
            'vault_id': vault_id,
            'salt': salt,
            'encrypted_data': '',  # Empty - will be filled on first save
            'expires_at': expires_at
        }).execute()

        if result.data:
            return vault_id, f"Vault created! Your Vault ID is: {vault_id}"
        else:
            return None, "Failed to create vault. Please try again."

    except Exception as e:
        return None, f"Error: {str(e)}"


# =============================================================================
# LOVABLE TO STREAMLIT DATA TRANSFORMER
# =============================================================================

def transform_lovable_to_streamlit(lovable_data: dict) -> dict:
    """
    Transform Lovable INTAKE data format to Streamlit session_state format.

    Lovable uses nested objects: profile.name, income.salary.current, etc.
    Streamlit uses flat keys: input_user_name, input_salary_wages, etc.

    Args:
        lovable_data: Data from Lovable INTAKE (nested format)

    Returns:
        Streamlit-compatible flat dictionary with input_* keys
    """
    from datetime import datetime

    result = {}

    # Helper to safely get nested values (returns float for numeric fields)
    def get_nested(obj, *keys, default=0.0):
        for key in keys:
            if obj is None or not isinstance(obj, dict):
                return float(default)
            obj = obj.get(key)
        # Ensure numeric values are returned as float for st.number_input compatibility
        if obj is None:
            return float(default)
        try:
            return float(obj)
        except (ValueError, TypeError):
            return float(default)

    # ==========================================================================
    # PROFILE
    # ==========================================================================
    profile = lovable_data.get('profile', {})
    result['input_user_name'] = profile.get('name', '')

    # Calculate age from birth year
    birth_year = profile.get('birthYear')
    if birth_year:
        result['input_age'] = datetime.now().year - birth_year
    else:
        result['input_age'] = 0

    # Partner info
    relationship = profile.get('relationshipStatus')
    result['input_partner_exists'] = relationship not in [None, 'single', '']
    result['input_partner_name'] = profile.get('partnerName', '')
    result['input_retirement_age'] = profile.get('retirementAgeUser') or 65

    # ==========================================================================
    # INCOME
    # ==========================================================================
    income = lovable_data.get('income', {})
    result['input_salary_wages'] = get_nested(income, 'salary', 'current', default=0)
    result['input_self_employment_income'] = get_nested(income, 'selfEmployment', 'current', default=0)
    result['input_social_security_income'] = get_nested(income, 'socialSecurity', 'current', default=0)
    result['input_pension_income'] = get_nested(income, 'pension', 'current', default=0)
    result['input_rental_income'] = get_nested(income, 'rentalIncome', 'current', default=0)
    result['input_investment_income'] = get_nested(income, 'investmentIncome', 'current', default=0)
    result['input_other_income'] = get_nested(income, 'otherIncome', 'current', default=0)

    # Calculate total income
    result['input_total_income'] = (
        result['input_salary_wages'] +
        result['input_self_employment_income'] +
        result['input_social_security_income'] +
        result['input_pension_income'] +
        result['input_rental_income'] +
        result['input_investment_income'] +
        result['input_other_income']
    )

    # ==========================================================================
    # EXPENSES
    # ==========================================================================
    expenses = lovable_data.get('expenses', {})
    result['input_housing_expenses'] = get_nested(expenses, 'housing', 'amount', default=0)
    result['input_utilities_expenses'] = get_nested(expenses, 'utilities', 'amount', default=0)
    result['input_groceries_expenses'] = get_nested(expenses, 'groceries', 'amount', default=0)
    result['input_transportation_expenses'] = get_nested(expenses, 'transportation', 'amount', default=0)
    result['input_healthcare_expenses'] = get_nested(expenses, 'healthcare', 'amount', default=0)
    result['input_insurance_expenses'] = get_nested(expenses, 'insurance', 'amount', default=0)
    result['input_entertainment_expenses'] = get_nested(expenses, 'entertainment', 'amount', default=0)
    result['input_restaurant_expenses'] = get_nested(expenses, 'diningOut', 'amount', default=0)
    result['input_travel_expenses'] = get_nested(expenses, 'travel', 'amount', default=0)
    result['input_education_expenses'] = get_nested(expenses, 'education', 'amount', default=0)
    result['input_childcare_expenses'] = get_nested(expenses, 'childcare', 'amount', default=0)
    result['input_clothing_expenses'] = get_nested(expenses, 'clothing', 'amount', default=0)
    result['input_charitable_donations'] = get_nested(expenses, 'charity', 'amount', default=0)
    result['input_miscellaneous_expenses'] = get_nested(expenses, 'miscellaneous', 'amount', default=0)
    result['input_other_expenses'] = get_nested(expenses, 'other', 'amount', default=0)

    # Calculate total expenses
    result['input_total_expenses'] = (
        result['input_housing_expenses'] +
        result['input_utilities_expenses'] +
        result['input_groceries_expenses'] +
        result['input_transportation_expenses'] +
        result['input_healthcare_expenses'] +
        result['input_insurance_expenses'] +
        result['input_entertainment_expenses'] +
        result['input_restaurant_expenses'] +
        result['input_travel_expenses'] +
        result['input_education_expenses'] +
        result['input_childcare_expenses'] +
        result['input_clothing_expenses'] +
        result['input_charitable_donations'] +
        result['input_miscellaneous_expenses'] +
        result['input_other_expenses']
    )

    # ==========================================================================
    # ASSETS
    # ==========================================================================
    assets = lovable_data.get('assets', {})
    result['input_high_yield_savings_account'] = get_nested(assets, 'checkingSavings', 'currentValue', default=0)
    result['input_four01k_403b_balance'] = get_nested(assets, 'retirement401k', 'currentValue', default=0)
    result['input_ira_balance'] = get_nested(assets, 'iraAccounts', 'currentValue', default=0)
    result['input_taxable_investment_accounts'] = get_nested(assets, 'brokerageAccounts', 'currentValue', default=0)
    result['input_primary_residence_value'] = get_nested(assets, 'realEstatePrimary', 'currentValue', default=0)
    result['input_secondary_residence_value'] = get_nested(assets, 'realEstateInvestment', 'currentValue', default=0)
    result['input_business_ownership_value'] = get_nested(assets, 'businessEquity', 'currentValue', default=0)
    result['input_vehicles_value'] = get_nested(assets, 'vehicles', 'currentValue', default=0)
    result['input_hsa_balance'] = get_nested(assets, 'hsa', 'currentValue', default=0)
    result['input_five29_plan_balance'] = get_nested(assets, 'education529', 'currentValue', default=0)
    result['input_jewelry_collectibles_value'] = get_nested(assets, 'collectibles', 'currentValue', default=0)
    result['input_cryptocurrency_holdings'] = get_nested(assets, 'crypto', 'currentValue', default=0)
    result['input_other_assets'] = get_nested(assets, 'otherAssets', 'currentValue', default=0)

    # ==========================================================================
    # LIABILITIES
    # ==========================================================================
    liabilities = lovable_data.get('liabilities', {})
    result['input_mortgage_balance'] = get_nested(liabilities, 'mortgage', 'balance', default=0)
    result['input_auto_loan_balance'] = get_nested(liabilities, 'autoLoans', 'balance', default=0)
    result['input_student_loan_balance'] = get_nested(liabilities, 'studentLoans', 'balance', default=0)
    result['input_credit_card_debt'] = get_nested(liabilities, 'creditCards', 'balance', default=0)
    result['input_other_liabilities'] = get_nested(liabilities, 'otherDebts', 'balance', default=0)

    # ==========================================================================
    # FAMILY: CHILDREN
    # ==========================================================================
    family = lovable_data.get('family', {})
    lovable_children = family.get('children', [])

    children_list = []
    for child in lovable_children:
        children_list.append({
            'Name': child.get('name', 'Child'),
            'Birth Year': child.get('birthYear', 2010),
            'College Plan': child.get('educationPlan') or 'Public In-State',
            'Scholarship %': 0.0,
            'Start Age': 18,
            'Years': 4,
            'Use 529 First?': True
        })

    result['children_list'] = children_list
    result['children_rows'] = children_list  # Streamlit uses both

    # ==========================================================================
    # FAMILY: INHERITANCES
    # ==========================================================================
    lovable_inheritances = family.get('inheritances', [])

    inheritance_list = []
    for inh in lovable_inheritances:
        inheritance_list.append({
            'Year': inh.get('expectedYear', 2030),
            'Amount': float(inh.get('estimatedAmount', 0)),
            'Taxable?': False
        })

    result['inheritance_list'] = inheritance_list
    result['inherit_rows'] = inheritance_list  # Streamlit uses both

    # ==========================================================================
    # FAMILY: GOALS
    # ==========================================================================
    lovable_goals = family.get('goals', [])

    goals_list = []
    for goal in lovable_goals:
        goals_list.append({
            'Goal': goal.get('description', 'Financial Goal'),
            'Target $': float(goal.get('targetAmount', 0)),
            'Target Year': float(goal.get('targetYear', 2030)),
            'goal': goal.get('description', 'Financial Goal'),
            'amount': float(goal.get('targetAmount', 0)),
            'year': goal.get('targetYear', 2030)
        })

    result['goals_list'] = goals_list
    result['goals_data'] = goals_list  # Streamlit uses both

    # ==========================================================================
    # METADATA
    # ==========================================================================
    result['_lovable_source'] = True  # Mark as transformed from Lovable
    result['_lovable_mode'] = lovable_data.get('mode', 'unknown')
    result['_lovable_plan_name'] = lovable_data.get('planName', '')

    return result


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
        raw_data = json.loads(decrypted_json)

        # Check if this is Lovable format (has 'profile' key) or Streamlit format (has 'input_' keys)
        if 'profile' in raw_data:
            # Lovable format - transform to Streamlit format
            print(f"[VAULT] Detected Lovable format - transforming to Streamlit format...")
            data = transform_lovable_to_streamlit(raw_data)
            print(f"[VAULT] Transformation complete. Keys: {len(data)}")
        else:
            # Already Streamlit format
            data = raw_data

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
# AUTO-SYNC HELPER (for background sync after local save)
# =============================================================================

def auto_sync_to_cloud(data: dict) -> Tuple[bool, str]:
    """
    Automatically sync data to cloud if user has credentials in session.

    This is called after local save to keep cloud in sync.
    Requires cloud_password to be in session_state (set during restore).

    Args:
        data: The intake data dict to sync

    Returns:
        (success, message) - Returns (True, "No cloud backup") if not configured
    """
    import streamlit as st

    # DEBUG: What data is being synced?
    print(f"☁️ SYNC DEBUG - Total keys: {len(data.keys())}")
    print(f"☁️ SYNC DEBUG - input_age: {data.get('input_age', 'MISSING')}")
    print(f"☁️ SYNC DEBUG - input_salary_wages: {data.get('input_salary_wages', 'MISSING')}")
    print(f"☁️ SYNC DEBUG - input_housing_expenses: {data.get('input_housing_expenses', 'MISSING')}")
    print(f"☁️ SYNC DEBUG - input_ira_balance: {data.get('input_ira_balance', 'MISSING')}")

    # Check if we have credentials for sync
    password = st.session_state.get('cloud_password')
    if not password:
        print("☁️ SYNC: No cloud_password in session - auto-sync requires restore first")
        return True, "No cloud backup configured (need to restore first)"

    vault_id = st.session_state.get('vault_id')
    email = st.session_state.get('user_email')

    print(f"☁️ SYNC DEBUG - vault_id: {vault_id}, email: {email}")

    if vault_id:
        # Sync to anonymous vault
        print(f"🔄 AUTO-SYNC: Syncing to vault {vault_id}...")
        success, message = update_anonymous_vault(vault_id, password, data)
        if success:
            print(f"✅ AUTO-SYNC: Vault updated successfully")
        else:
            print(f"❌ AUTO-SYNC: Failed - {message}")
        return success, message

    elif email:
        # Sync to user vault
        print(f"🔄 AUTO-SYNC: Syncing to user vault for {email}...")
        success, message = update_user_vault(email, password, data)
        if success:
            print(f"✅ AUTO-SYNC: User vault updated successfully")
        else:
            print(f"❌ AUTO-SYNC: Failed - {message}")
        return success, message

    return True, "No cloud backup configured"


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
