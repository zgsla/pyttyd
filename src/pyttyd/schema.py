
from pydantic import BaseModel, Field

class WdtModel(BaseModel):
    token: str = Field(...)
