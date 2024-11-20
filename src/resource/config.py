from pydantic import (
    BaseModel,
    SecretStr,
)


class SecretKey(BaseModel):
    SECRET_KEY: SecretStr = b'_5#y2L"F4Q8z\n\xec]/'


class database(BaseModel):
    pass
