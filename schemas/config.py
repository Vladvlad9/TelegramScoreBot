from pydantic import BaseModel


class BotSchema(BaseModel):
    TOKEN: str
    ADMINS: list[int]


class SupportSchema(BaseModel):
    PHONE: str
    INSTAGRAM: str
    EMAIL: str
    DISCORD: str
    TELEGRAM: str


class ConfigSchema(BaseModel):
    BOT: BotSchema
    DATABASE: str
    SUPPORT: SupportSchema
