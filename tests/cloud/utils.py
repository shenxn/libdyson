"""Utilities for cloud tests."""

import base64
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from libdyson.cloud.utils import DYSON_ENCRYPTION_INIT_VECTOR, DYSON_ENCRYPTION_KEY


def encrypt_credential(serial: str, credential: str) -> str:
    """Encrypt device local credential."""
    data = {
        "serial": serial,
        "apPasswordHash": credential,
    }
    data = json.dumps(data)
    padded_length = (len(data) + 15) // 16 * 16
    if padded_length > len(data):
        n_pad = padded_length - len(data)
        data += chr(n_pad) * n_pad
    data = data.encode("utf-8")
    cipher = Cipher(
        algorithms.AES(DYSON_ENCRYPTION_KEY),
        modes.CBC(DYSON_ENCRYPTION_INIT_VECTOR),
    )
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode("utf-8")
