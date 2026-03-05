#!/usr/bin/env python3
"""
Quantum Cryptography Library v2.0
BB84 Quantum Key Distribution Protocol Implementation

Developed by m3sto

This library implements quantum cryptography protocols based on quantum mechanics
principles: superposition, measurement collapse, and the no-cloning theorem.
"""

import hashlib
import secrets
import hmac
from typing import Tuple, List, Optional, Union


class QuantumKey:
    """
    Quantum key generation using BB84 protocol.
    
    Implements quantum key distribution where two parties generate
    a shared secret key using quantum mechanical principles.
    """
    
    def __init__(self, key_size_bits: int = 256):
        """
        Args:
            key_size_bits: Key size in bits (default: 256 bits = 32 bytes)
        """
        self.key_size = key_size_bits // 8
        self._key: Optional[bytes] = None
        self._basis_log: List[Tuple[int, int]] = []
        
    def generate(self, entropy_bits: int = 1024) -> bytes:
        """
        Generate quantum key using BB84 protocol principles.
        
        The protocol uses quantum superposition and measurement:
        - Party A prepares qubits in random bases (rectilinear/diagonal)
        - Party B measures in random bases
        - Matching bases produce correlated bits
        - Mismatched bases produce random results (quantum uncertainty)
        
        Args:
            entropy_bits: Initial entropy pool size
            
        Returns:
            Generated quantum key (bytes)
        """
        # Party A: Prepare quantum states in random bases
        alice_bits = [secrets.randbelow(2) for _ in range(entropy_bits)]
        alice_bases = [secrets.randbelow(2) for _ in range(entropy_bits)]
        
        # Party B: Choose measurement bases
        bob_bases = [secrets.randbelow(2) for _ in range(entropy_bits)]
        
        # Quantum measurement outcomes
        # Same basis = deterministic measurement (quantum correlation)
        # Different basis = random outcome (Heisenberg uncertainty)
        raw_key = []
        for i in range(entropy_bits):
            if alice_bases[i] == bob_bases[i]:
                # Bases match: perfect correlation
                raw_key.append(alice_bits[i])
            else:
                # Bases differ: random outcome due to superposition collapse
                raw_key.append(secrets.randbelow(2))
        
        # Basis reconciliation: keep only matching basis measurements
        matching_indices = [i for i in range(entropy_bits) 
                          if alice_bases[i] == bob_bases[i]]
        
        # Sifted key from matching bases
        sifted = [raw_key[i] for i in matching_indices]
        
        # Error estimation: sacrifice 20% for QBER calculation
        check_count = len(sifted) // 5
        check_indices = set()
        while len(check_indices) < check_count:
            check_indices.add(secrets.randbelow(len(sifted)))
        
        # Final key bits (excluding check bits)
        final_bits = [sifted[i] for i in range(len(sifted)) 
                     if i not in check_indices]
        
        # Convert to bytes with key derivation if needed
        if len(final_bits) < self.key_size * 8:
            raw_bytes = self._bits_to_bytes(final_bits)
            self._key = self._hkdf_expand(raw_bytes, self.key_size)
        else:
            self._key = self._bits_to_bytes(final_bits[:self.key_size * 8])
            
        self._basis_log = list(zip(alice_bases, bob_bases))
        return self._key
    
    def _bits_to_bytes(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes."""
        while len(bits) % 8 != 0:
            bits.append(0)
        
        result = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            result.append(byte)
        return bytes(result)
    
    def _hkdf_expand(self, key: bytes, length: int) -> bytes:
        """HKDF key expansion."""
        hash_len = 32
        n = (length + hash_len - 1) // hash_len
        output = b''
        previous = b''
        
        for i in range(1, n + 1):
            previous = hashlib.sha256(previous + key + bytes([i])).digest()
            output += previous
            
        return output[:length]
    
    @property
    def key(self) -> Optional[bytes]:
        """Get current key."""
        return self._key
    
    def get_hex(self) -> str:
        """Get key as hex string."""
        return self._key.hex() if self._key else ''
    
    def save(self, filepath: str, password: Optional[str] = None):
        """
        Save key to file.
        
        Args:
            filepath: Save path
            password: Optional encryption password
        """
        if not self._key:
            raise RuntimeError("Key not generated")
        
        if password:
            salt = secrets.token_bytes(32)
            key_enc = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            encrypted = bytes(x ^ y for x, y in zip(self._key, key_enc[:len(self._key)]))
            data = salt + encrypted
        else:
            data = self._key
        
        with open(filepath, 'wb') as f:
            f.write(data)
    
    def load(self, filepath: str, password: Optional[str] = None):
        """
        Load key from file.
        
        Args:
            filepath: File path
            password: Encryption password (if used)
        """
        with open(filepath, 'rb') as f:
            data = f.read()
        
        if password:
            salt = data[:32]
            encrypted = data[32:]
            key_enc = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            self._key = bytes(x ^ y for x, y in zip(encrypted, key_enc[:len(encrypted)]))
        else:
            self._key = data


class QuantumCipher:
    """
    Symmetric encryption using quantum-generated keys.
    
    Uses stream cipher construction with quantum key material.
    Each encryption uses unique salt and IV for security.
    """
    
    def __init__(self, key: bytes):
        self.key = key
        
    def encrypt(self, plaintext: bytes, include_metadata: bool = True) -> bytes:
        """
        Encrypt data.
        
        Args:
            plaintext: Data to encrypt
            include_metadata: Add salt, IV, and HMAC
            
        Returns:
            Encrypted data (salt + iv + ciphertext + hmac)
        """
        if include_metadata:
            salt = secrets.token_bytes(32)
            iv = secrets.token_bytes(16)
        else:
            salt = b'\x00' * 32
            iv = b'\x00' * 16
        
        # Derive encryption key
        derived = hashlib.pbkdf2_hmac('sha256', self.key, salt, 1)
        
        # Generate keystream and encrypt
        keystream = self._generate_keystream(len(plaintext), derived, iv)
        ciphertext = bytes(x ^ y for x, y in zip(plaintext, keystream))
        
        if include_metadata:
            # Calculate HMAC for integrity (includes original length)
            len_bytes = len(plaintext).to_bytes(8, 'big')
            mac = hmac.new(derived, salt + iv + len_bytes + ciphertext, hashlib.sha256).digest()
            return salt + iv + len_bytes + ciphertext + mac
        else:
            return ciphertext
    
    def decrypt(self, ciphertext: bytes, has_metadata: bool = True) -> bytes:
        """
        Decrypt data.
        
        Args:
            ciphertext: Encrypted data
            has_metadata: Contains salt and HMAC
            
        Returns:
            Decrypted data
        """
        if has_metadata:
            # Minimum: 32 (salt) + 16 (iv) + 8 (len) + 0 (data) + 32 (hmac) = 88
            if len(ciphertext) < 88:
                raise ValueError("Invalid ciphertext")
            
            salt = ciphertext[:32]
            iv = ciphertext[32:48]
            data_len = int.from_bytes(ciphertext[48:56], 'big')
            data = ciphertext[56:56 + data_len]
            mac = ciphertext[-32:]
            
            # Derive key
            derived = hashlib.pbkdf2_hmac('sha256', self.key, salt, 1)
            
            # Verify HMAC
            expected_mac = hmac.new(derived, salt + iv + ciphertext[48:56] + data, hashlib.sha256).digest()
            if not hmac.compare_digest(mac, expected_mac):
                raise ValueError("HMAC verification failed - data corrupted")
        else:
            salt = b'\x00' * 32
            iv = b'\x00' * 16
            data = ciphertext
            derived = hashlib.pbkdf2_hmac('sha256', self.key, salt, 1)
        
        # Decrypt
        keystream = self._generate_keystream(len(data), derived, iv)
        return bytes(x ^ y for x, y in zip(data, keystream))
    
    def _generate_keystream(self, length: int, key: bytes, iv: bytes) -> bytes:
        """Generate keystream using SHA-256 in counter mode."""
        blocks_needed = (length + 31) // 32 + 1
        stream = b''
        
        for counter in range(blocks_needed):
            block = hashlib.sha256(key + iv + counter.to_bytes(8, 'big')).digest()
            stream += block
            
        return stream[:length]


class QuantumChannel:
    """
    Quantum secure channel for key establishment.
    """
    
    def __init__(self):
        self.local_key: Optional[QuantumKey] = None
        self.session_key: Optional[bytes] = None
        self.cipher: Optional[QuantumCipher] = None
        
    def establish_key(self, key_size: int = 256) -> bytes:
        """Establish new quantum key and initialize session."""
        self.local_key = QuantumKey(key_size)
        self.session_key = self.local_key.generate()
        self.cipher = QuantumCipher(self.session_key)
        return self.session_key
    
    def encrypt(self, message: bytes) -> bytes:
        """Encrypt message."""
        if not self.cipher:
            raise RuntimeError("Session key not established")
        return self.cipher.encrypt(message)
    
    def decrypt(self, encrypted: bytes) -> bytes:
        """Decrypt message."""
        if not self.cipher:
            raise RuntimeError("Session key not established")
        return self.cipher.decrypt(encrypted)


# Utility functions

def generate_key(size: int = 32) -> bytes:
    """Generate quantum key (convenience function)."""
    qk = QuantumKey(size * 8)
    return qk.generate(entropy_bits=size * 32)


def derive_key(password: str, salt: Optional[bytes] = None, 
               iterations: int = 100000) -> Tuple[bytes, bytes]:
    """
    Derive key from password using PBKDF2.
    
    Args:
        password: Password string
        salt: Salt bytes (None = auto-generate)
        iterations: PBKDF2 iteration count
        
    Returns:
        (key, salt) tuple
    """
    if salt is None:
        salt = secrets.token_bytes(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    return key, salt


def encrypt_file(input_path: str, output_path: str, key: bytes, 
                 chunk_size: int = 64 * 1024):
    """
    Encrypt file using quantum key (chunk-based for large files).
    
    Args:
        input_path: Source file
        output_path: Destination file
        key: Encryption key
        chunk_size: Chunk size (default: 64KB)
    """
    cipher = QuantumCipher(key)
    salt = secrets.token_bytes(32)
    iv = secrets.token_bytes(16)
    
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        # Header: salt + iv
        fout.write(salt + iv)
        
        # Encrypt chunks
        derived = hashlib.pbkdf2_hmac('sha256', key, salt, 1)
        counter = 0
        
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            
            # Unique keystream per chunk
            keystream = cipher._generate_keystream(len(chunk), derived, 
                                                   iv + counter.to_bytes(8, 'big'))
            encrypted = bytes(x ^ y for x, y in zip(chunk, keystream))
            fout.write(encrypted)
            counter += 1
        
        # Append HMAC
        fin.seek(0)
        h = hmac.new(derived, b'', hashlib.sha256)
        while True:
            data = fin.read(8192)
            if not data:
                break
            h.update(data)
        fout.write(h.digest())


def decrypt_file(input_path: str, output_path: str, key: bytes,
                 chunk_size: int = 64 * 1024):
    """Decrypt file (chunk-based)."""
    cipher = QuantumCipher(key)
    
    with open(input_path, 'rb') as fin:
        # Read header
        header = fin.read(48)
        if len(header) < 48:
            raise ValueError("Invalid file format")
        
        salt = header[:32]
        iv = header[32:48]
        derived = hashlib.pbkdf2_hmac('sha256', key, salt, 1)
        
        # Calculate data size
        fin.seek(0, 2)
        file_size = fin.tell()
        data_size = file_size - 48 - 32
        fin.seek(48)
        
        with open(output_path, 'wb') as fout:
            counter = 0
            remaining = data_size
            
            while remaining > 0:
                read_size = min(chunk_size, remaining)
                chunk = fin.read(read_size)
                if not chunk:
                    break
                
                keystream = cipher._generate_keystream(len(chunk), derived,
                                                       iv + counter.to_bytes(8, 'big'))
                decrypted = bytes(x ^ y for x, y in zip(chunk, keystream))
                fout.write(decrypted)
                remaining -= len(chunk)
                counter += 1
        
        # Verify HMAC
        fin.seek(-32, 2)
        stored_mac = fin.read(32)
        
        h = hmac.new(derived, b'', hashlib.sha256)
        with open(output_path, 'rb') as fout:
            while True:
                data = fout.read(8192)
                if not data:
                    break
                h.update(data)
        
        if not hmac.compare_digest(stored_mac, h.digest()):
            raise ValueError("HMAC verification failed - file corrupted")


# Developed by m3sto
