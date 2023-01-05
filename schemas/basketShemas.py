from pydantic import BaseModel, Field


class BasketSchema(BaseModel):

    pizza_id: int = Field(ge=1)
    count: int = Field(ge=1, default=1)
    user_id: int = Field(default=None)


class BasketInDBSchema(BasketSchema):
    id: int = Field(ge=1)
