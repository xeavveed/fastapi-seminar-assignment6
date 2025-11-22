from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)
from typing import Optional

from wapang.common.exceptions import (
    InvalidFormatException,
    MissingRequiredFieldException,
)


class ReviewCreate(BaseModel):
    rating: int
    comment: str

    @field_validator("rating")
    def validate_rating(cls, v) -> int:
        if v < 1 or v > 5:
            raise InvalidFormatException()
        return v

    @field_validator("comment")
    def validate_comment(cls, v) -> str:
        if len(v) > 500:
            raise InvalidFormatException()
        return v
    
class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None

    @field_validator("rating")
    def validate_rating(cls, v) -> int:
        if v is not None and (v < 1 or v > 5):
            raise InvalidFormatException()
        return v

    @field_validator("comment")
    def validate_comment(cls, v) -> str:
        if v is not None and len(v) > 500:
            raise InvalidFormatException()
        return v

    @model_validator(mode="after")
    def at_least_one_field(self):
        if self.rating is None and self.comment is None:
            raise MissingRequiredFieldException()
        return self

class ReviewLogoutResponse(BaseModel):
    review_id: str
    item_id: str
    writer_nickname: str
    rating: int
    comment: str

class ReviewLoginResponse(BaseModel):
    review_id: str
    item_id: str
    writer_nickname: str
    is_writer: bool
    rating: int
    comment: str