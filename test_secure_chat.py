import unittest
import os
from crypto_utils import CryptoManager
from server import ChatServer

class TestCryptoManager(unittest.TestCase):

    def setUp(self):
        self.key_material = "test_shared_secret"
        self.crypto = CryptoManager(self.key_material)

    def test_encrypt_decrypt(self):
        message = "Hello Secure World"
        encrypted = self.crypto.encrypt(message)
        decrypted = self.crypto.decrypt(encrypted)
        self.assertEqual(message, decrypted)

    def test_encryption_changes_text(self):
        message = "Sensitive Data"
        encrypted = self.crypto.encrypt(message)
        self.assertNotEqual(message.encode(), encrypted)

    def test_wrong_key_fails(self):
        message = "Secret"
        encrypted = self.crypto.encrypt(message)

        wrong_crypto = CryptoManager("wrong_key")
        with self.assertRaises(Exception):
            wrong_crypto.decrypt(encrypted)


class TestServerUserManagement(unittest.TestCase):

    def setUp(self):
        self.server = ChatServer("127.0.0.1", 9999)
        self.test_username = "test_user"

        # Ensure clean environment
        if os.path.exists("server_storage/users.txt"):
            os.remove("server_storage/users.txt")

    def test_save_user(self):
        self.server.save_user(self.test_username)
        users = self.server.load_users()
        self.assertIn(self.test_username, users)


if __name__ == "__main__":
    unittest.main()