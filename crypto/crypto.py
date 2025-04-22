from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

KEYS_DIR = "crypto/keys"
os.makedirs(KEYS_DIR, exist_ok=True)

def load_key_from_file(path=f"{KEYS_DIR}/ARIA_AES_KEY.txt"):
    with open(path, "r") as f:
        for line in f:
            if line.startswith("ARIA_AES_KEY="):
                return base64.b64decode(line.split("=", 1)[1].strip())
    raise ValueError("Key not found in key file.")

def generate_keys():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    if os.path.exists(f"{KEYS_DIR}/private.pem"):
        print("[!] Keys already exist. Skipping generation.")
        return
    with open(f"{KEYS_DIR}/private.pem", "wb") as f:
        f.write(priv.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))
    with open(f"{KEYS_DIR}/public.pem", "wb") as f:
        f.write(pub.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_keys():
    with open(f"{KEYS_DIR}/private.pem", "rb") as f:
        priv = serialization.load_pem_private_key(f.read(), password=None)
    with open(f"{KEYS_DIR}/public.pem", "rb") as f:
        pub = serialization.load_pem_public_key(f.read())
    return priv, pub

def encrypt_message(key: bytes, plaintext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, plaintext, None)

def decrypt_message(key: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ct = ciphertext[12:]
    return aesgcm.decrypt(nonce, ct, None)

if __name__ == "__main__":
    generate_keys()
    try:
        priv, pub = load_keys()
    except FileNotFoundError:
        print("[!] Keys not found. Generating...")
        generate_keys()
        priv, pub = load_keys()
    print("[+] Keys generated and loaded.")
    # Example usage
    shared_key = os.urandom(32)  # Replace with your actual shared key
    message = b"Hello, World!"
    encrypted = encrypt_message(shared_key, message)
    decrypted = decrypt_message(shared_key, encrypted)
    print("[+] Original:", message)
    print("[+] Encrypted:", encrypted)
    print("[+] Decrypted:", decrypted)