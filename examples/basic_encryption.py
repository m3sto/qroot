#!/usr/bin/env python3
"""
Basic Encryption Example
Developed by m3sto

Demonstrates quantum key generation and message encryption.
"""

import sys
sys.path.insert(0, '..')

from qroot import generate_key, QuantumCipher


def main():
    # Generate quantum key
    print("Generating quantum key...")
    key = generate_key(32)
    print(f"Key: {key.hex()}")
    
    # Create cipher
    cipher = QuantumCipher(key)
    
    # Encrypt message
    message = b"Secret message using quantum cryptography"
    print(f"\nOriginal: {message.decode()}")
    
    encrypted = cipher.encrypt(message)
    print(f"Encrypted: {encrypted.hex()}")
    
    # Decrypt message
    decrypted = cipher.decrypt(encrypted)
    print(f"Decrypted: {decrypted.decode()}")
    
    # Verify
    assert message == decrypted, "Decryption failed"
    print("\nSuccess: Message encrypted and decrypted correctly")


if __name__ == "__main__":
    main()
