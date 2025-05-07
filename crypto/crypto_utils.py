# AES utilities (from previous crypto.py)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_message(key, message):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, message.encode('utf-8'), None)
    return nonce + ciphertext

def decrypt_message(key, encrypted_message):
    aesgcm = AESGCM(key)
    nonce = encrypted_message[:12]
    ciphertext = encrypted_message[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')