from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)
from typing import Optional

from wapang.common.exceptions import (
    InvalidFormatException,
    MissingRequiredFieldException,
)


class ProductResponse(BaseModel):
    id: str
    name: str = Field(serialization_alias="item_name")
    price: int
    stock: int
    store_id: str

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: str
    item_name: str
    price: int
    stock: int
    store_id: str
    store_name: str

    class Config:
        from_attributes = True


class ItemCreateRequest(BaseModel):
    item_name: str
    price: int
    stock: int

    @field_validator("item_name")
    def validate_item_name(cls, v) -> str:
        if len(v) < 2 or len(v) > 50:
            raise InvalidFormatException()
        return v

    @field_validator("price")
    def validate_price(cls, v) -> int:
        if v < 0:
            raise InvalidFormatException()
        return v

    @field_validator("stock")
    def validate_stock(cls, v) -> int:
        if v < 0:
            raise InvalidFormatException()
        return v


class ItemUpdateRequest(BaseModel):
    item_name: Optional[str] = None
    price: Optional[int] = None
    stock: Optional[int] = None

    @field_validator("item_name")
    def validate_item_name(cls, v) -> str:
        if v is not None and (len(v) < 2 or len(v) > 50):
            raise InvalidFormatException()
        return v

    @field_validator("price")
    def validate_price(cls, v) -> int:
        if v is not None and v < 0:
            raise InvalidFormatException()
        return v

    @field_validator("stock")
    def validate_stock(cls, v) -> int:
        if v is not None and v < 0:
            raise InvalidFormatException()
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.item_name is None and self.price is None and self.stock is None:
            raise MissingRequiredFieldException()
        return self
