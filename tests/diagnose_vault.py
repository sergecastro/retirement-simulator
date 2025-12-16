"""
Vault Diagnostic Script
=======================
Reads and decrypts a vault from Supabase to inspect the actual data structure.

Usage:
    python tests/diagnose_vault.py FF-P5ZJ-RZJ5 YourPassword123
"""

import sys
import json
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.supabase_sync import get_supabase_client
from utils.password_crypto import decrypt_with_password


def diagnose_vault(vault_id: str, password: str):
    """Fetch and decrypt a vault, showing the actual data structure."""

    print("=" * 60)
    print(f"VAULT DIAGNOSTIC: {vault_id}")
    print("=" * 60)

    # Step 1: Fetch from Supabase
    print("\n[1] Fetching vault from Supabase...")
    client = get_supabase_client()
    result = client.table('anonymous_vaults').select('*').eq('vault_id', vault_id.upper()).execute()

    if not result.data:
        print(f"[ERROR] Vault {vault_id} not found!")
        return

    vault = result.data[0]
    print(f"    Vault ID: {vault['vault_id']}")
    print(f"    Salt length: {len(vault['salt'])} chars")
    print(f"    Encrypted data length: {len(vault['encrypted_data'])} chars")
    print(f"    Expires at: {vault['expires_at']}")

    # Step 2: Check if encrypted_data is empty
    if not vault['encrypted_data']:
        print("\n[ERROR] encrypted_data is EMPTY! No data was saved.")
        return

    print(f"    First 50 chars of encrypted_data: {vault['encrypted_data'][:50]}...")

    # Step 3: Attempt decryption
    print("\n[2] Attempting decryption...")
    try:
        decrypted_json = decrypt_with_password(
            vault['encrypted_data'],
            password,
            vault['salt']
        )
        print("    [OK] Decryption successful!")
    except Exception as e:
        print(f"    [ERROR] Decryption failed: {e}")
        return

    # Step 4: Parse JSON
    print("\n[3] Parsing JSON...")
    try:
        data = json.loads(decrypted_json)
        print(f"    [OK] Valid JSON with {len(data)} keys")
    except Exception as e:
        print(f"    [ERROR] JSON parse failed: {e}")
        print(f"    Raw decrypted text: {decrypted_json[:200]}...")
        return

    # Step 5: Show all keys
    print("\n[4] Data structure (all keys):")
    print("-" * 40)
    for key in sorted(data.keys()):
        value = data[key]
        value_preview = str(value)[:50] if len(str(value)) > 50 else str(value)
        print(f"    {key}: {value_preview}")

    # Step 6: Check for expected Streamlit fields
    print("\n[5] Checking for expected Streamlit fields:")
    print("-" * 40)

    expected_fields = [
        'input_user_name',
        'input_age',
        'input_salary_wages',
        'input_social_security',
        'input_housing_expenses',
        'input_savings_balance',
        'input_ira_balance',
        'input_401k_balance',
    ]

    for field in expected_fields:
        if field in data:
            print(f"    [OK] {field}: {data[field]}")
        else:
            print(f"    [MISSING] {field}")

    # Step 7: Show full JSON (pretty printed)
    print("\n[6] Full decrypted data (JSON):")
    print("-" * 40)
    print(json.dumps(data, indent=2))

    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tests/diagnose_vault.py <vault_id> <password>")
        print("Example: python tests/diagnose_vault.py FF-P5ZJ-RZJ5 MyPassword123")
        sys.exit(1)

    vault_id = sys.argv[1]
    password = sys.argv[2]

    diagnose_vault(vault_id, password)
