from datetime import datetime
from pydantic import BaseModel, Field


class TypeSchema(BaseModel):
    name: str = Field(default=None)


class TypeInDBSchema(TypeSchema):
    id: int = Field(ge=1)
