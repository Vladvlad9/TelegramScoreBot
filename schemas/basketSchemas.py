from datetime import datetime
from pydantic import BaseModel, Field


class BasketSchema(BaseModel):

    pizza_id: int
    count: int
    user_id: int


class BasketInDBSchema(BasketSchema):
    id: int = Field(ge=1)
