"""
Crypto Compatibility Test: JavaScript (Web Crypto API) <-> Python
==================================================================
This test verifies that Web Crypto API output can be decrypted by our Python code.

Architecture D requires Lovable (React) to encrypt data client-side using Web Crypto,
then Streamlit (Python) decrypts it. This test proves bit-exact compatibility.

Usage:
    1. Run: python tests/test_js_python_crypto.py
    2. Copy the JavaScript code to browser console
    3. Copy the encrypted output back to this file
    4. Run again to verify decryption
"""

import base64
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.password_crypto import (
    decrypt_with_password,
    encrypt_with_password,
    generate_salt,
    SALT_LENGTH,
    NONCE_LENGTH,
    PBKDF2_ITERATIONS
)


# =============================================================================
# TEST CONSTANTS - These must match between Python and JavaScript
# =============================================================================

TEST_PASSWORD = "TestPassword123!"

# Generate a deterministic 32-byte salt for testing (base64 encoded)
# This is exactly 32 bytes (count carefully!)
TEST_SALT_BYTES = b"testsalt123456789012345678901234"  # Exactly 32 bytes
TEST_SALT_BASE64 = base64.b64encode(TEST_SALT_BYTES).decode('utf-8')

TEST_PLAINTEXT = {"name": "Test User", "age": 60, "income": 5000}
TEST_PLAINTEXT_JSON = json.dumps(TEST_PLAINTEXT)


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_python_encrypt_decrypt():
    """Verify Python encryption/decryption works correctly."""
    print("\n" + "=" * 60)
    print("TEST 1: Python Encrypt -> Python Decrypt")
    print("=" * 60)

    # Encrypt
    encrypted = encrypt_with_password(TEST_PLAINTEXT_JSON, TEST_PASSWORD, TEST_SALT_BASE64)
    print(f"[OK] Encrypted length: {len(encrypted)} chars")
    print(f"   First 50 chars: {encrypted[:50]}...")

    # Decrypt
    decrypted = decrypt_with_password(encrypted, TEST_PASSWORD, TEST_SALT_BASE64)
    decrypted_data = json.loads(decrypted)

    assert decrypted_data == TEST_PLAINTEXT, f"Mismatch! Got {decrypted_data}"
    print(f"[OK] Decrypted successfully: {decrypted_data}")
    print("[OK] TEST 1 PASSED: Python crypto works correctly")

    return encrypted


def test_decrypt_from_javascript():
    """
    Test decryption of JavaScript-generated ciphertext.

    STEP 1: Run this test with encrypted_from_js = None to see expected format
    STEP 2: Paste JavaScript-generated encrypted string here
    STEP 3: Run test again to verify decryption works
    """
    print("\n" + "=" * 60)
    print("TEST 2: JavaScript Encrypt -> Python Decrypt")
    print("=" * 60)

    # =========================================================================
    # JavaScript output from browser test (Dec 15, 2025)
    # =========================================================================
    encrypted_from_js = "wKnFaNEI1dC8Wmbqyaa1OU9GowwpDEkHSpr17K7Q3i9UA8b2s2QNi4t5U4KQ0iLDej5Tyw0ds8GNQJdHyciG/7wHaWO/8/I="

    if encrypted_from_js is None:
        print("\n[!] No JavaScript ciphertext provided yet.")
        print("\nTo complete this test:")
        print("1. Copy the JavaScript code printed below")
        print("2. Open browser DevTools (F12) -> Console")
        print("3. Paste and run the code")
        print("4. Copy the encrypted output")
        print("5. Paste it in this file (encrypted_from_js variable)")
        print("6. Run this test again")
        print("\n" + "-" * 60)
        print("JAVASCRIPT TEST CODE:")
        print("-" * 60)
        print(generate_js_test_code())
        print("-" * 60)
        return False

    # Attempt decryption
    try:
        decrypted = decrypt_with_password(encrypted_from_js, TEST_PASSWORD, TEST_SALT_BASE64)
        decrypted_data = json.loads(decrypted)

        print(f"[OK] DECRYPTION SUCCESSFUL!")
        print(f"   Decrypted: {decrypted_data}")

        assert decrypted_data == TEST_PLAINTEXT, f"Data mismatch! Expected {TEST_PLAINTEXT}, got {decrypted_data}"
        print("[OK] DATA MATCHES PERFECTLY!")
        print("[OK] TEST 2 PASSED: JavaScript -> Python crypto is compatible!")
        return True

    except Exception as e:
        print(f"[FAIL] DECRYPTION FAILED: {e}")
        print("\nDebugging info:")
        print(f"   Password: {TEST_PASSWORD}")
        print(f"   Salt (base64): {TEST_SALT_BASE64}")
        print(f"   Expected plaintext: {TEST_PLAINTEXT_JSON}")
        raise


def generate_js_test_code():
    """Generate JavaScript code to run in browser console."""

    # Convert salt bytes to JavaScript array format
    salt_array = list(TEST_SALT_BYTES)

    js_code = f'''
// =============================================================================
// CRYPTO COMPATIBILITY TEST - Run in Browser Console (Chrome DevTools -> Console)
// =============================================================================
// This code encrypts test data using Web Crypto API
// The output should decrypt successfully in Python
// =============================================================================

(async function() {{
  console.log("Starting encryption test...");

  // Test parameters (MUST match Python)
  const password = "{TEST_PASSWORD}";
  const plaintext = {json.dumps(TEST_PLAINTEXT)};

  // Use the SAME salt as Python test (32 bytes)
  const saltBytes = new Uint8Array({salt_array});
  console.log("Salt length:", saltBytes.length, "bytes (expected: 32)");

  const enc = new TextEncoder();
  const data = enc.encode(JSON.stringify(plaintext));
  console.log("Plaintext length:", data.length, "bytes");

  // Generate 12-byte IV (nonce)
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  console.log("IV length:", iv.length, "bytes (expected: 12)");

  // Import password as key material
  const keyMaterial = await window.crypto.subtle.importKey(
    "raw",
    enc.encode(password),
    {{ name: "PBKDF2" }},
    false,
    ["deriveKey"]
  );
  console.log("Key material imported");

  // Derive AES-256 key using PBKDF2 (600,000 iterations)
  console.log("Deriving key with 600,000 PBKDF2 iterations (may take a moment)...");
  const startTime = performance.now();

  const key = await window.crypto.subtle.deriveKey(
    {{
      name: "PBKDF2",
      salt: saltBytes,
      iterations: {PBKDF2_ITERATIONS},
      hash: "SHA-256",
    }},
    keyMaterial,
    {{ name: "AES-GCM", length: 256 }},
    false,
    ["encrypt"]
  );

  const keyDerivationTime = performance.now() - startTime;
  console.log("Key derived in", Math.round(keyDerivationTime), "ms");

  // Encrypt with AES-256-GCM
  const encryptedContent = await window.crypto.subtle.encrypt(
    {{ name: "AES-GCM", iv: iv }},
    key,
    data
  );
  console.log("Encrypted content length:", encryptedContent.byteLength, "bytes");
  console.log("  (includes 16-byte auth tag)");

  // Combine: IV (12 bytes) + Ciphertext + AuthTag
  // This matches Python format: nonce + ciphertext
  const encryptedBytes = new Uint8Array(encryptedContent);
  const combined = new Uint8Array(iv.length + encryptedBytes.length);
  combined.set(iv);
  combined.set(encryptedBytes, iv.length);
  console.log("Combined length:", combined.length, "bytes");
  console.log("  = 12 (IV) +", encryptedBytes.length, "(ciphertext+tag)");

  // Convert to Base64
  const encrypted_data = btoa(String.fromCharCode(...combined));

  console.log("");
  console.log("=".repeat(60));
  console.log("SUCCESS! Copy the string below to Python test:");
  console.log("=".repeat(60));
  console.log("");
  console.log(encrypted_data);
  console.log("");
  console.log("=".repeat(60));
  console.log("Paste this as: encrypted_from_js = \\"" + encrypted_data + "\\"");
  console.log("=".repeat(60));

  return encrypted_data;
}})();
'''
    return js_code


def print_test_parameters():
    """Print all test parameters for verification."""
    print("\n" + "=" * 60)
    print("TEST PARAMETERS")
    print("=" * 60)
    print(f"Password:        {TEST_PASSWORD}")
    print(f"Salt (bytes):    {TEST_SALT_BYTES}")
    print(f"Salt (base64):   {TEST_SALT_BASE64}")
    print(f"Salt length:     {len(TEST_SALT_BYTES)} bytes (required: {SALT_LENGTH})")
    print(f"Nonce length:    {NONCE_LENGTH} bytes")
    print(f"PBKDF2 iters:    {PBKDF2_ITERATIONS:,}")
    print(f"Plaintext:       {TEST_PLAINTEXT}")
    print(f"Plaintext JSON:  {TEST_PLAINTEXT_JSON}")
    print("=" * 60)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CRYPTO COMPATIBILITY TEST: JavaScript <-> Python")
    print("Architecture D Validation")
    print("=" * 60)

    # Print parameters
    print_test_parameters()

    # Test 1: Python self-test
    try:
        test_python_encrypt_decrypt()
    except Exception as e:
        print(f"[FAIL] TEST 1 FAILED: {e}")
        sys.exit(1)

    # Test 2: JavaScript -> Python
    try:
        js_test_passed = test_decrypt_from_javascript()
        if js_test_passed:
            print("\n" + "=" * 60)
            print("*** ALL TESTS PASSED! ***")
            print("Architecture D crypto compatibility is VERIFIED.")
            print("You can proceed with Lovable implementation.")
            print("=" * 60)
    except Exception as e:
        print(f"[FAIL] TEST 2 FAILED: {e}")
        sys.exit(1)
