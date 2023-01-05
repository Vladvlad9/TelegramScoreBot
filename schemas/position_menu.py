from pydantic import BaseModel, Field


class PositionMenuSchema(BaseModel):
    name: str = Field(default=None)


class PositionMenuInDBSchema(PositionMenuSchema):
    id: int = Field(ge=1)
