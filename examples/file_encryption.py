#!/usr/bin/env python3
"""
File Encryption Example
Developed by m3sto

Demonstrates encrypting and decrypting files.
"""

import sys
sys.path.insert(0, '..')

from qroot import generate_key, encrypt_file, decrypt_file


def main():
    # Generate quantum key
    key = generate_key(32)
    print(f"Generated key: {key.hex()[:64]}...")
    
    # Create test file
    filename = "secret_data.txt"
    with open(filename, 'w') as f:
        f.write("This is confidential data.\n" * 100)
    print(f"\nCreated test file: {filename}")
    
    # Encrypt file
    encrypt_file(filename, "encrypted_data.bin", key)
    print("File encrypted: encrypted_data.bin")
    
    # Decrypt file
    decrypt_file("encrypted_data.bin", "decrypted_data.txt", key)
    print("File decrypted: decrypted_data.txt")
    
    # Verify
    with open(filename, 'rb') as f:
        original = f.read()
    with open("decrypted_data.txt", 'rb') as f:
        decrypted = f.read()
    
    assert original == decrypted, "File decryption failed"
    print("\nSuccess: File encrypted and decrypted correctly")


if __name__ == "__main__":
    main()
