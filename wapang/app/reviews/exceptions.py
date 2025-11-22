from wapang.common.exceptions import WapangException


class ReviewAlreadyExistsException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409, 
            error_code="ERR_016", 
            error_msg="REVIEW ALREADY EXISTS"
        )

class ReviewNotFoundException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404, 
            error_code="ERR_022", 
            error_msg="REVIEW NOT FOUND"
        )

class NotYourReviewException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403, 
            error_code="ERR_023", 
            error_msg="NOT YOUR REVIEW"
        )