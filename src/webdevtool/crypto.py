import datetime
import random
import base64
from typing import Union

from cryptography import x509
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asy_padding
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    BestAvailableEncryption,
    load_pem_private_key,
    load_pem_public_key
)


class RSAPrivateKey:

    def __init__(self, key: Union[rsa.RSAPrivateKey, bytes]):
        if isinstance(key, rsa.RSAPrivateKey):
            self._key = key
            self._text = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        else:
            self._key = load_pem_private_key(key, None)
            self._text = key

    def decrypt(self, sign):
        # return rsa.decrypt(sign, self.pv_key)
        return self._key.decrypt(sign, padding=asy_padding.PKCS1v15())


class RSAPublicKey:

    def __init__(self, pb_text):
        self.pb_text = pb_text
        # self.pb_key = rsa.PublicKey.load_pkcs1(pb_text)
        self.pb_key = load_pem_public_key(self.pb_text)

    def encrypt(self, text):
        # return rsa.encrypt(text, self.pb_key)
        return self.pb_key.encrypt(text, padding=asy_padding.PKCS1v15())


class RSAKey:

    def __init__(self, public_exponent: int, key_size: int):
        self.public_exponent = public_exponent
        self.key_size = key_size

        self.pv_key = rsa.generate_private_key(self.public_exponent, self.key_size)
        self.pb_key = self.pv_key.public_key()
        # self.pb_key, self.pv_key = rsa.newkeys(self.key_size, poolsize=2)

    def pb_text(self):
        # return self.pb_key.save_pkcs1()
        return self.pb_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )

    def pv_text(self):
        # return self.pv_key.save_pkcs1()
        return self.pv_key.private_bytes(
            Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()
        )

    def encrypt(self, text):
        # return rsa.encrypt(text, self.pb_key)
        return self.pb_key.encrypt(text, padding=asy_padding.PKCS1v15())

    def decrypt(self, sign):
        # return rsa.decrypt(sign, self.pv_key)
        return self.pv_key.decrypt(base64.b64decode(sign), padding=asy_padding.PKCS1v15())


class RSAKeyPool:

    def __init__(self, size: int):
        self.size = size
        self._keys = {}
        self.gen_keys()
        self._kk = list(self._keys)

    def gen_keys(self):
        for _ in range(self.size):
            rk = RSAKey(65537, 2048)
            self._keys[rk.pb_text()] = rk.pv_text()

    def random_choice_pb_text(self):
        return random.choice(self._kk)

    def get_pv_text(self, pb_text):
        return self._keys.get(pb_text)

    def decrypt(self, pb_text, sign):
        if not self._keys.get(pb_text):
            return
        pv_key = RSAPrivateKey(self._keys[pb_text])
        return pv_key.decrypt(base64.b64decode(sign))

    def encrypt(self, text):
        pb_text = self.random_choice_pb_text()
        pb_key = RSAPublicKey(pb_text)
        return pb_text, pb_key.encrypt(text)


class AESCrypto:

    def __init__(self, key, iv):
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        self._pkcs7 = padding.PKCS7(algorithms.AES.block_size)

    def decrypt(self, encrypted):
        dec = self._cipher.decryptor()
        unpadder = self._pkcs7.unpadder()
        unpadder_data = base64.b64decode(encrypted)
        data = unpadder.update(dec.update(unpadder_data))
        try:
            uppadded_data = data + unpadder.finalize()
        except ValueError:
            raise Exception('无效的加密信息!')

        return uppadded_data.decode('utf8')

    def encrypt(self, src):
        enc = self._cipher.encryptor()
        padder = self._pkcs7.padder()
        padded_data = padder.update(src) + padder.finalize()

        padded_data = enc.update(padded_data)
        return base64.b64encode(padded_data)


rsa_key = RSAKey(65537, 2048)
# rsa_pool = RSAKeyPool(100)


if __name__ == '__main__':
    pass
