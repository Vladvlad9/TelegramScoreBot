from datetime import datetime
from pydantic import BaseModel, Field


class PizzaMenuSchema(BaseModel):
    photo: bytes
    description: str = Field(default="Нет описания")
    name: str = Field(default=None)
    type_id: int = Field(ge=1)
    price: str = Field(default=1)
    size_id: int = Field(ge=1)


class PizzaMenuSchemaInDBSchema(PizzaMenuSchema):
    id: int = Field(ge=1)
