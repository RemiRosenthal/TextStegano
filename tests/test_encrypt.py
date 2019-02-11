import unittest

from cryptography.fernet import Fernet

from stegano.encrypt import Encryptor


class TestEncrypt(unittest.TestCase):
    def setUp(self):
        self.key = bytes(b'xqKRXGO5RO7JLxE_jAHmA9L_uolEOjDvcGYBo2AgapM=')
        self.encryptor = Encryptor(self.key)

    def test_encrypt_bytes(self):
        data = str.encode("Hello", "utf-16")
        self.assertEqual(data, b'\xff\xfeH\x00e\x00l\x00l\x00o\x00')
        token = self.encryptor.encrypt_bytes(data)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, bytes)

    def test_encrypt_bytes_unicode(self):
        data = str.encode("ह𐍈", "utf-16")
        self.assertEqual(data, b'\xff\xfe9\t\x00\xd8H\xdf')
        token = self.encryptor.encrypt_bytes(data)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, bytes)

    def test_decrypt(self):
        f = Fernet(self.key)
        token = f.encrypt(b'\xff\xfe9\t\x00\xd8H\xdf')
        text = self.encryptor.decrypt(token)
        self.assertEqual(text, b'\xff\xfe9\t\x00\xd8H\xdf')

    def test_symmetric_encryption(self):
        data = bytes(b'\xff\xfeH\x00e\x00l\x00l\x00o\x00')
        tokens = set()
        for x in range(0, 5):
            tokens.add(self.encryptor.encrypt_bytes(data))
        for token in tokens:
            decrypted = self.encryptor.decrypt(token)
            self.assertEqual(decrypted, data)

    if __name__ == '__main__':
        unittest.main()
