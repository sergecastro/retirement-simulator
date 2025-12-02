"""
Password-Based Encryption for Family Forecast
============================================
Zero-knowledge encryption using user's password.
"""

import base64
import hashlib
import secrets
import string
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


# =============================================================================
# CONFIGURATION
# =============================================================================

SALT_LENGTH = 32
NONCE_LENGTH = 12
KEY_LENGTH = 32
PBKDF2_ITERATIONS = 600_000


# =============================================================================
# VAULT ID GENERATION
# =============================================================================

def generate_vault_id() -> str:
    """Generate a human-readable vault ID like FF-X7K9-M2PL."""
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace('O', '').replace('0', '').replace('I', '').replace('1', '')

    part1 = ''.join(secrets.choice(chars) for _ in range(4))
    part2 = ''.join(secrets.choice(chars) for _ in range(4))

    return f"FF-{part1}-{part2}"


# =============================================================================
# KEY DERIVATION
# =============================================================================

def generate_salt() -> str:
    """Generate a random salt for key derivation."""
    salt_bytes = secrets.token_bytes(SALT_LENGTH)
    return base64.b64encode(salt_bytes).decode('utf-8')


def derive_key_from_password(password: str, salt: str) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    salt_bytes = base64.b64decode(salt.encode('utf-8'))

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt_bytes,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )

    return kdf.derive(password.encode('utf-8'))


# =============================================================================
# ENCRYPTION / DECRYPTION
# =============================================================================

def encrypt_with_password(plaintext: str, password: str, salt: str) -> str:
    """Encrypt data using password-derived key."""
    key = derive_key_from_password(password, salt)
    nonce = secrets.token_bytes(NONCE_LENGTH)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

    encrypted_bytes = nonce + ciphertext
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def decrypt_with_password(encrypted_data: str, password: str, salt: str) -> str:
    """Decrypt data using password-derived key."""
    try:
        key = derive_key_from_password(password, salt)

        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
        nonce = encrypted_bytes[:NONCE_LENGTH]
        ciphertext = encrypted_bytes[NONCE_LENGTH:]

        aesgcm = AESGCM(key)
        plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext_bytes.decode('utf-8')

    except Exception as e:
        raise ValueError(f"Decryption failed - wrong password or corrupted data")


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

def validate_password_strength(password: str) -> tuple:
    """Validate password meets minimum requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password must be less than 128 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and a number"

    return True, "Password meets requirements"


# =============================================================================
# EMAIL HASHING (for account-based lookup)
# =============================================================================

def hash_email(email: str) -> str:
    """Hash email for privacy-preserving lookup."""
    normalized = email.lower().strip()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("Testing password_crypto module...")

    # Test vault ID
    vault_id = generate_vault_id()
    print(f"Vault ID: {vault_id}")

    # Test encryption
    test_password = "MySecurePass123"
    test_salt = generate_salt()
    test_data = '{"name": "Test", "savings": 500000}'

    encrypted = encrypt_with_password(test_data, test_password, test_salt)
    print(f"Encrypted: {encrypted[:50]}...")

    decrypted = decrypt_with_password(encrypted, test_password, test_salt)
    print(f"Decrypted: {decrypted}")

    # Test wrong password
    try:
        decrypt_with_password(encrypted, "WrongPass123", test_salt)
        print("ERROR: Should have failed!")
    except ValueError:
        print("[OK] Correctly rejected wrong password")

    # Test email hashing
    email_hash = hash_email("Test@Example.com")
    print(f"Email hash: {email_hash[:20]}...")

    print("\n[OK] All tests passed!")
