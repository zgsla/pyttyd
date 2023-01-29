import json
import base64

from fastapi import Header, Cookie

from webdevtool.crypto import rsa_key, AESCrypto


class CryptoDepend:

    def __init__(self, auth: str = Header(default=None), session=Cookie(default=None)):
        aess = auth or session
        if not aess:
            raise ValueError
        aes_pass = json.loads(rsa_key.decrypt(aess).decode('utf8'))
        aes_key = base64.b64decode(aes_pass['key'])
        aes_iv = base64.b64decode(aes_pass['iv'])
        self.aes_crypto = AESCrypto(aes_key, aes_iv)

    def decrypt(self, encrypted):
        return self.aes_crypto.decrypt(encrypted)

    def encrypt(self, src):
        return self.aes_crypto.encrypt(src)
