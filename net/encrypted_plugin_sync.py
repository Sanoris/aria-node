import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from memory.tagger import log_tagged_memory
from net.plugin_receiver import receive_plugin

def decrypt_plugin(enc_data, key_b64):
    key = base64.b64decode(key_b64)
    aesgcm = AESGCM(key)
    nonce = enc_data[:12]
    return aesgcm.decrypt(nonce, enc_data[12:], None).decode()

def handle_incoming_plugin(enc_data, key_b64, filename, peer_ip, trusted_peers):
    if peer_ip not in trusted_peers:
        log_tagged_memory(f"Rejected plugin from untrusted {peer_ip}", topic="plugin", trust="low")
        return
    try:
        code = decrypt_plugin(enc_data, key_b64)
        receive_plugin(base64.b64encode(code.encode()).decode(), filename, peer_ip)
        log_tagged_memory(f"Accepted plugin from {peer_ip}", topic="plugin", trust="high")
    except Exception as e:
        log_tagged_memory(f"Failed to handle encrypted plugin from {peer_ip}: {e}", topic="plugin", trust="low")
