from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
import os

KEY_DIR = "crypto/keys"
os.makedirs(KEY_DIR, exist_ok=True)

def generate_keypair():
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    with open(f"{KEY_DIR}/private.pem", "wb") as f:
        f.write(priv.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))
    with open(f"{KEY_DIR}/public.pem", "wb") as f:
        f.write(pub.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_private_key():
    with open(f"{KEY_DIR}/private.pem", "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)

def load_public_key():
    with open(f"{KEY_DIR}/public.pem", "rb") as f:
        return serialization.load_pem_public_key(f.read())

def sign_message(data: bytes) -> bytes:
    priv = load_private_key()
    return priv.sign(data)

def verify_signature(public_key: Ed25519PublicKey, message: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False

# Ensure keys are generated on first load
if not os.path.exists(f"{KEY_DIR}/private.pem") or not os.path.exists(f"{KEY_DIR}/public.pem"):
    generate_keypair()
