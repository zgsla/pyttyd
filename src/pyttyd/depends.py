import json
import base64
import datetime

from fastapi import Query, Header, Cookie, Body

from pyttyd.crypto import rsa_key, AESCrypto
from pyttyd.schema import WdtModel


class CryptoDepend:

    def __init__(
        self,
        token: str = Query(default=None),
        auth: str = Header(default=None),
        session: str = Cookie(default=None),
        body: WdtModel = Body(default=None)
    ):
        encrypted = auth or session

        if not encrypted:
            raise ValueError
        # print(base64.b64decode(encrypted))
        aes = json.loads(rsa_key.decrypt(base64.b64decode(encrypted)).decode('utf8'))
        # print(aes)
        self._token = token if token else body.token if body else None

        self._cryptor = AESCrypto(
            base64.b64decode(aes['key']),
            base64.b64decode(aes['iv'])
        )

    @property
    def token(self):
        return self._token

    @property
    def source(self):
        return self.decrypt(self._token)

    def json(self):
        return json.loads(self.source)

    def decrypt(self, encrypted):
        return self._cryptor.decrypt(encrypted)

    def encrypt(self, src):
        return self._cryptor.encrypt(src)


def to_dict(row):
    dct = {}
    for k, v in row.items():
        if isinstance(v, datetime.datetime):
            dct[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        else:
            dct[k] = v
    return dct
