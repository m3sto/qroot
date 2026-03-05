#!/usr/bin/env python3
"""
Key Management Example
Developed by m3sto

Demonstrates saving and loading encrypted keys.
"""

import sys
sys.path.insert(0, '..')

from qroot import QuantumKey, QuantumCipher


def main():
    # Generate quantum key
    print("Generating quantum key...")
    qk = QuantumKey(256)
    key = qk.generate()
    print(f"Key: {key.hex()[:64]}...")
    
    # Save key with password protection
    password = "my_secure_password_123"
    qk.save("my_key.bin", password=password)
    print("\nKey saved with password protection: my_key.bin")
    
    # Load key
    print("\nLoading key...")
    qk2 = QuantumKey(256)
    qk2.load("my_key.bin", password=password)
    loaded_key = qk2.key
    print(f"Loaded key: {loaded_key.hex()[:64]}...")
    
    # Verify keys match
    assert key == loaded_key, "Key loading failed"
    print("\nSuccess: Key saved and loaded correctly")
    
    # Use loaded key for encryption
    cipher = QuantumCipher(loaded_key)
    message = b"Test with loaded key"
    encrypted = cipher.encrypt(message)
    decrypted = cipher.decrypt(encrypted)
    
    assert message == decrypted, "Encryption with loaded key failed"
    print("Success: Encryption with loaded key works")


if __name__ == "__main__":
    main()
