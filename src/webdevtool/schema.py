from pydantic import BaseModel, Field


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
