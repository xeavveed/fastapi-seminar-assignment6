from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    model_validator,
)
from typing import Optional
from typing_extensions import Annotated

from wapang.common.exceptions import (
    InvalidFormatException,
    MissingRequiredFieldException,
)
from wapang.app.stores.exceptions import InvalidFieldFormatException
import re


class NewStoreRequest(BaseModel):
    store_name: str
    address: str
    email: EmailStr
    phone_number: str
    delivery_fee: int

    @field_validator("store_name", mode="after")
    def validate_store_name(cls, v) -> str:
        if len(v) < 3 or len(v) > 20:
            raise InvalidFormatException()
        return v

    @field_validator("address", mode="after")
    def validate_address(cls, v) -> str:
        if len(v) > 100:
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
        
    @field_validator("delivery_fee", mode="after")
    def validate_delivery_fee(cls, v) -> int:
        if v < 0:
            raise InvalidFieldFormatException()
        return v


class ChangeStoreRequest(BaseModel):
    store_name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    delivery_fee: Optional[int] = None

    @field_validator("store_name", mode="after")
    def validate_store_name(cls, v) -> str:
        if v is not None and (len(v) < 3 or len(v) > 20):
            raise InvalidFormatException()
        return v
    
    @field_validator("address", mode="after")
    def validate_address(cls, v) -> str:
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
        
    @field_validator("delivery_fee", mode="after")
    def validate_delivery_fee(cls, v) -> int:
        if v < 0:
            raise InvalidFieldFormatException()
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.store_name is None and self.address is None and self.email is None and self.phone_number is None and self.delivery_fee is None:
            raise MissingRequiredFieldException()
        return self


class StoreResponse(BaseModel):
    id: str
    store_name: str
    address: str
    email: EmailStr
    phone_number: str
    delivery_fee: int

    @field_validator("store_name", mode="after")
    def validate_store_name(cls, v) -> str:
        if len(v) < 3 or len(v) > 20:
            raise InvalidFormatException()
        return v
    
    @field_validator("address", mode="after")
    def validate_address(cls, v) -> str:
        if len(v) > 100:
            raise InvalidFormatException()
        return v

    class Config:
        from_attributes = True
