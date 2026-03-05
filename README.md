# qroot

Quantum Cryptography Library implementing BB84 Quantum Key Distribution Protocol.

Developed by m3sto

## Overview

qroot implements quantum cryptography using quantum mechanical principles:
- **Superposition**: Quantum states exist in multiple bases simultaneously
- **Measurement Collapse**: Observation affects quantum states
- **No-Cloning Theorem**: Quantum states cannot be perfectly copied

The BB84 protocol enables two parties to generate a shared secret key with information-theoretic security.

## Installation

```bash
# Clone repository
git clone https://github.com/m3sto/qroot.git
cd qroot/v2

# No dependencies required - pure Python 3.8+
```

## Quick Start

```python
from qroot import generate_key, QuantumCipher

# Generate quantum key
key = generate_key(32)

# Encrypt data
cipher = QuantumCipher(key)
encrypted = cipher.encrypt(b"secret message")

# Decrypt data
decrypted = cipher.decrypt(encrypted)
```

## Features

- **BB84 Protocol**: Quantum key distribution with basis reconciliation
- **Stream Cipher**: SHA-256 based keystream generation
- **Authenticated Encryption**: Salt, IV, and HMAC for integrity
- **Password Protection**: PBKDF2 for key encryption
- **Large File Support**: Chunk-based processing

## API Reference

### QuantumKey

```python
from qroot import QuantumKey

qk = QuantumKey(256)  # 256-bit key
key = qk.generate()

# Save with password
qk.save("key.bin", password="secret")

# Load with password
qk2 = QuantumKey(256)
qk2.load("key.bin", password="secret")
```

### QuantumCipher

```python
from qroot import QuantumCipher

cipher = QuantumCipher(key)
encrypted = cipher.encrypt(plaintext)
decrypted = cipher.decrypt(encrypted)
```

### File Operations

```python
from qroot import encrypt_file, decrypt_file

encrypt_file("input.txt", "output.enc", key)
decrypt_file("output.enc", "input.txt", key)
```

### QuantumChannel

```python
from qroot import QuantumChannel

channel = QuantumChannel()
channel.establish_key(256)
encrypted = channel.encrypt(message)
decrypted = channel.decrypt(encrypted)
```

## Examples

See `examples/` directory:
- `basic_encryption.py` - Message encryption
- `file_encryption.py` - File encryption
- `key_management.py` - Key save/load
- `secure_channel.py` - Secure communication

Run examples:
```bash
cd examples
python3 basic_encryption.py
```

## Security

- Uses `secrets` module for cryptographically secure randomness
- PBKDF2 with 100,000 iterations for password derivation
- HMAC-SHA256 for integrity verification
- Unique salt and IV per encryption

## Requirements

- Python 3.8+
- No external dependencies

## License

MIT License

## Developer

Developed by m3sto

For questions and contributions, contact the developer.
