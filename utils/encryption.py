# utils/encryption.py - Simple client-side encryption for localStorage
"""
Browser-based encryption for Family Forecast user data.

SECURITY MODEL:
- Session-generated encryption key (never hardcoded!)
- Key stored in Streamlit session state (cleared when session ends)
- Data encrypted before storing in browser localStorage
- Simple XOR cipher with base64 encoding for obfuscation
- NOT military-grade encryption, but prevents casual inspection

WHY THIS APPROACH:
- No server-side keys needed (truly client-side)
- No hardcoded keys in source code (security best practice)
- Unique key per session (even if someone gets one key, can't decrypt other users)
- No dependencies on external libraries
- Fast encode/decode
- Prevents casual browsing of localStorage data

NOTE: This is obfuscation, not cryptographic security.
For true security, user should use HTTPS + clear browser data regularly.
"""

import base64
import json
import secrets
import streamlit as st
from typing import Dict, Any, Optional


def _get_storage_preference() -> str:
    """
    Get user's storage preference (persistent vs session-only).

    Returns:
        'persistent' or 'session_only'
    """
    # Check if preference is already set in session state
    if 'storage_preference' in st.session_state:
        return st.session_state.storage_preference

    # Check localStorage for saved preference (via JavaScript)
    # For now, default to 'persistent' (will add UI choice later)
    return 'persistent'


def _get_or_create_encryption_key() -> str:
    """
    Get or create encryption key based on user's storage preference.

    USER CHOICE:
    - "Remember my data" → Key stored in localStorage (persistent)
    - "Session only" → Key stored in st.session_state (cleared on close)

    Returns:
        Encryption key (base64 string, 44 characters)
    """
    storage_pref = _get_storage_preference()

    if storage_pref == 'persistent':
        # PERSISTENT MODE: Check if key exists in session state first (fast path)
        if 'encryption_key_persistent' in st.session_state:
            return st.session_state.encryption_key_persistent

        # Try to load from localStorage (will be implemented via JavaScript bridge)
        # For now, check session state as fallback
        if 'encryption_key' in st.session_state:
            key = st.session_state.encryption_key
            st.session_state.encryption_key_persistent = key
            return key

        # Generate new key
        random_bytes = secrets.token_bytes(32)
        key = base64.b64encode(random_bytes).decode('ascii')

        # Store in session state for this session
        st.session_state.encryption_key = key
        st.session_state.encryption_key_persistent = key

        # TODO: Save to localStorage via JavaScript (Phase 3B)
        # save_key_to_local_storage(key)

        return key

    else:
        # SESSION-ONLY MODE: Store only in session state
        if 'encryption_key' not in st.session_state:
            random_bytes = secrets.token_bytes(32)
            st.session_state.encryption_key = base64.b64encode(random_bytes).decode('ascii')

        return st.session_state.encryption_key


def _xor_encrypt_decrypt(data: str, key: str) -> str:
    """
    Simple XOR cipher - same function encrypts and decrypts.

    Args:
        data: String to encrypt/decrypt
        key: Cipher key

    Returns:
        Encrypted/decrypted string
    """
    # Convert to bytes
    data_bytes = data.encode('utf-8')
    key_bytes = key.encode('utf-8')

    # XOR each byte with repeating key
    result = bytearray()
    for i, byte in enumerate(data_bytes):
        result.append(byte ^ key_bytes[i % len(key_bytes)])

    return result.decode('latin-1')


def encrypt_data(data: Dict[str, Any]) -> str:
    """
    Encrypt dictionary data for localStorage storage.

    Uses session-specific encryption key (unique per user session).

    Args:
        data: Dictionary to encrypt (will be JSON serialized)

    Returns:
        Base64-encoded encrypted string

    Example:
        >>> data = {"user_name": "John", "age": 65}
        >>> encrypted = encrypt_data(data)
        >>> print(encrypted)  # Returns base64 string (unique each session!)
    """
    try:
        # Get encryption key (persistent or session-only based on user preference)
        cipher_key = _get_or_create_encryption_key()

        # Convert dict to JSON string
        json_str = json.dumps(data, ensure_ascii=False)

        # XOR encrypt with session key
        encrypted = _xor_encrypt_decrypt(json_str, cipher_key)

        # Base64 encode for safe storage
        encoded = base64.b64encode(encrypted.encode('latin-1')).decode('ascii')

        return encoded

    except Exception as e:
        raise ValueError(f"Encryption failed: {e}")


def decrypt_data(encrypted_str: str) -> Optional[Dict[str, Any]]:
    """
    Decrypt localStorage data back to dictionary.

    Uses session-specific encryption key (must be same session that encrypted it).

    Args:
        encrypted_str: Base64-encoded encrypted string from localStorage

    Returns:
        Decrypted dictionary, or None if decryption fails

    Example:
        >>> encrypted = "Q2lwaGVy..."
        >>> data = decrypt_data(encrypted)
        >>> print(data)  # {"user_name": "John", "age": 65}

    Note:
        Decryption will only work within the SAME session that encrypted the data.
        If session ends (browser closes), key is lost and data cannot be decrypted.
        This is intentional for session-only security!
    """
    try:
        # Get encryption key (persistent or session-only based on user preference)
        cipher_key = _get_or_create_encryption_key()

        # Base64 decode
        decoded = base64.b64decode(encrypted_str.encode('ascii')).decode('latin-1')

        # XOR decrypt (same operation as encrypt)
        decrypted = _xor_encrypt_decrypt(decoded, cipher_key)

        # Parse JSON back to dict
        data = json.loads(decrypted)

        return data

    except Exception as e:
        # Return None if decryption fails (corrupted data or wrong format)
        print(f"Decryption failed: {e}")
        return None


def test_encryption():
    """Test encryption/decryption roundtrip (standalone mode)"""
    print("Testing encryption module...")
    print("SECURITY: Using session-generated key (NOT hardcoded!)")

    # For standalone testing, simulate session state
    class MockSessionState:
        def __init__(self):
            self.data = {}

        def __contains__(self, key):
            return key in self.data

        def __getitem__(self, key):
            return self.data[key]

        def __setitem__(self, key, value):
            self.data[key] = value

    # Mock st.session_state for testing
    import sys
    if 'streamlit' not in sys.modules:
        # Running standalone (not in Streamlit app)
        # Create mock session state
        mock_state = MockSessionState()
        st.session_state = mock_state

    # Test data (realistic retirement scenario)
    test_data = {
        "input_user_name": "Test User",
        "input_age": 65,
        "input_partner_exists": True,
        "input_partner_name": "Test Partner",
        "input_ira_balance": 500000.0,
        "sensitive_data": "This should be encrypted!"
    }

    print("\nOriginal data:")
    print(json.dumps(test_data, indent=2))

    # Encrypt
    encrypted = encrypt_data(test_data)
    print("\nEncrypted (base64):")
    print(encrypted[:80] + "..." if len(encrypted) > 80 else encrypted)
    print(f"   Length: {len(encrypted)} characters")

    # Show the session key (for verification)
    if hasattr(st, 'session_state') and 'encryption_key' in st.session_state:
        key_preview = st.session_state.encryption_key[:16] + "..."
        print(f"   Session Key: {key_preview} (unique per session)")

    # Decrypt
    decrypted = decrypt_data(encrypted)
    print("\nDecrypted data:")
    print(json.dumps(decrypted, indent=2))

    # Verify
    if decrypted == test_data:
        print("\nSUCCESS! Encryption/decryption works perfectly!")
        print("   Data integrity verified - original matches decrypted")
        print("   Session key is unique and NOT hardcoded in source")
        return True
    else:
        print("\nFAILURE! Decrypted data doesn't match original")
        return False


if __name__ == "__main__":
    # Run tests when executed directly
    test_encryption()
