from cryptography.fernet import Fernet


class Encryptor:
    """
    Basic encryption class. Not guaranteed secure, but an encrypted bit stream
    is more "random", allowing for less predictable encoding.
    """

    def __init__(self, key):
        self.key = key

    @staticmethod
    def generate_key():
        return Fernet.generate_key()

    def encrypt_bytes(self, data: bytes) -> Fernet:
        """
        Encrypt some data into a Fernet token.

        :param data: bytes to encrypt
        :return: encrypted bytes
        """
        f = Fernet(self.key)
        token = f.encrypt(data)
        return token

    def encrypt_string(self, text: str) -> Fernet:
        """
        Encrypt a string into a Fernet token.

        :param text: string to encrypt
        :return: encrypted string
        """
        data = bytes(text, "utf-16")
        token = self.encrypt_bytes(data)
        return token

    def decrypt(self, token: Fernet) -> bytes:
        """
        Decrypt a Fernet token, revealing the original data.

        :param token: to decrypt
        :return: original data
        """
        f = Fernet(self.key)
        data = f.decrypt(token)
        return data
