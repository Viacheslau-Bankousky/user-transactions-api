from core.pydantic_base import BasePydanticModel


class Token(BasePydanticModel):
    access_token: str
    token_type: str
