import json

from fastapi import Header
from pydantic import BaseModel, Field

from pyttyd.crypto import AESCrypto, rsa_key


class CreateSSHConnectModel(BaseModel):
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    user: str = Field(...)
    password: str = Field(...)


class DeleteSSHConnectModel(BaseModel):
    ssh_id: int = Field(...)


class UpdateSSHConnectModel(BaseModel):
    ssh_id: int = Field(...)
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    user: str = Field(...)
    password: str = Field(None)


class WdtModel(BaseModel):
    token: str = Field(...)
