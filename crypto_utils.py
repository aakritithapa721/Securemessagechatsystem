from cryptography.fernet import Fernet
import hashlib
import base64

class CryptoManager:
    def __init__(self, key_material: str):
        digest = hashlib.sha256(key_material.encode()).digest()
        self.key = base64.urlsafe_b64encode(digest)
        self.fernet = Fernet(self.key)

    def encrypt(self, msg: str) -> bytes:
        return self.fernet.encrypt(msg.encode())

    def decrypt(self, token: bytes) -> str:
        return self.fernet.decrypt(token).decode()
