#!/usr/bin/env python3
"""
Secure Channel Example
Developed by m3sto

Demonstrates establishing a quantum secure channel.
"""

import sys
sys.path.insert(0, '..')

from qroot import QuantumChannel


def main():
    # Create secure channel
    channel = QuantumChannel()
    
    # Establish quantum key
    print("Establishing quantum key...")
    key = channel.establish_key(256)
    print(f"Session key established: {key.hex()[:64]}...")
    
    # Send encrypted messages
    messages = [
        b"Message 1: Hello",
        b"Message 2: Quantum encryption",
        b"Message 3: Secure communication"
    ]
    
    print("\nSending encrypted messages:")
    encrypted_messages = []
    for msg in messages:
        enc = channel.encrypt(msg)
        encrypted_messages.append(enc)
        print(f"  Sent: {msg.decode()}")
        print(f"  Encrypted: {enc.hex()[:48]}...")
    
    # Receive and decrypt
    print("\nReceiving and decrypting:")
    for i, enc in enumerate(encrypted_messages):
        dec = channel.decrypt(enc)
        print(f"  Received: {dec.decode()}")
        assert dec == messages[i], "Decryption failed"
    
    print("\nSuccess: All messages transmitted securely")


if __name__ == "__main__":
    main()
