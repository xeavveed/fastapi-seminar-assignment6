from pydantic import (
    BaseModel,
    EmailStr,
    StringConstraints,
    field_validator,
    model_validator,
)
from typing import Optional, Any
from typing_extensions import Annotated

from wapang.app.orders.models import OrderStatus
from wapang.common.exceptions import (
    InvalidFormatException,
    MissingRequiredFieldException,
)
from wapang.app.users.exceptions import InvalidFieldFormatException
import re


class UserSignupRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def validate_email_format(cls, v: str) -> str:
        pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not re.fullmatch(pattern, v):
            raise InvalidFieldFormatException()

        return v

    @field_validator("password", mode="after")
    def validate_password(cls, v) -> str:
        if len(v) < 8 or len(v) > 20:
            raise InvalidFormatException()
        return v


class UserChangeRequest(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def check_for_invalid_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        valid_fields = set(cls.model_fields.keys())
        received_keys = set(data.keys())

        invalid_keys = received_keys - valid_fields

        if invalid_keys:
            raise InvalidFormatException()

        return data

    @field_validator("nickname", mode="after")
    def validate_nickname(cls, v) -> Optional[str]:
        if v is not None and (len(v) < 2 or len(v) > 20):
            raise InvalidFormatException()
        return v

    @field_validator("address", mode="after")
    def validate_address(cls, v) -> Optional[str]:
        if v is not None and len(v) > 100:
            raise InvalidFormatException()
        return v

    @field_validator("phone_number", mode="after")
    def validate_phone(cls, v) -> Optional[str]:
        if v is None:
            return v
        pattern = re.compile("010-[0-9]{4}-[0-9]{4}")
        match = pattern.match(v)

        if match != None and match.span() == (0, len(v)):
            return v
        else:
            raise InvalidFormatException()

    @model_validator(mode="after")
    def at_least_one_field(self):
        if (
            self.email is None
            and self.nickname is None
            and self.address is None
            and self.phone_number is None
        ):
            raise MissingRequiredFieldException()
        return self


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    nickname: str | None
    address: str | None
    phone_number: str | None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    order_id: str
    total_price: int
    status: OrderStatus

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    review_id: str
    item_id: str
    item_name: str
    comment: str
    rating: int
