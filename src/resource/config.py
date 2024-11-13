from pydantic import (
    BaseModel,
    SecretBytes,
    SecretStr,
    ValidationError,
    field_serializer,
)


class SecretKey(BaseModel):
    SECRET_KEY: SecretStr

    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'



