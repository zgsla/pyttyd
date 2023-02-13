from typing import Optional

from pydantic import BaseModel, Field


class WdtModel(BaseModel):
    token: str = Field(...)


class BaseResponse(BaseModel):
    code: Optional[int] = Field(0)
    message: Optional[str] = Field("success")


class CommonResponse(BaseResponse):
    data: str = Field(...)
