from pydantic import BaseModel, Field


class CreateSSHConnectModel(BaseModel):
    name: str = Field(...)
    host: str = Field(...)
    port: int = Field(...)
    user: str = Field(...)
    password: str = Field(...)


class DeleteSSHConnectModel(BaseModel):
    id: int = Field(...)


class UpdateSSHConnectModel(CreateSSHConnectModel, DeleteSSHConnectModel):
    password: str = Field(None)
