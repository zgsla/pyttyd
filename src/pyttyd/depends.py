import json
import base64

from fastapi import Header, Cookie

from pyttyd.crypto import rsa_key, AESCrypto


class CryptoDepend:

    def __init__(self, auth: str = Header(default=None), session=Cookie(default=None)):
        encrypted = auth or session

        if not encrypted:
            raise ValueError

        aes = json.loads(rsa_key.decrypt(base64.b64decode(encrypted)).decode('utf8'))

        self.cryptor = AESCrypto(
            base64.b64decode(aes['key']),
            base64.b64decode(aes['iv'])
        )

    def decrypt(self, encrypted):
        return self.cryptor.decrypt(encrypted)

    def encrypt(self, src):
        return self.cryptor.encrypt(src)
