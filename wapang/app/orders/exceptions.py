from wapang.common.exceptions import WapangException


class MissingRequiredFieldsException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=400,
            error_code="ERR_002",
            error_msg="MISSING REQUIRED FIELDS"
        )
        
class InvalidFieldFormatException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=400,
            error_code="ERR_003",
            error_msg="INVALID FIELD FORMAT"
        )
        
class UnauthenticatedExceptionException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=401,
            error_code="ERR_005",
            error_msg="UNAUTHENTICATED"
        )

class BadAuthorizationHeaderException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=400,
            error_code="ERR_006",
            error_msg="BAD AUTHORIZATION HEADER"
        )

class InvalidTokenException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=401,
            error_code="ERR_007",
            error_msg="INVALID TOKEN"
        )
        
class ItemNotFoundException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=404,
            error_code="ERR_013",
            error_msg="ITEM NOT FOUND"
        )

class NotEnoughStockException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error_code="ERR_017",
            error_msg="NOT ENOUGH STOCK"
        )

class EmptyItemListException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=422,
            error_code="ERR_018",
            error_msg="EMPTY ITEM LIST"
        )
        
class OrderNotFoundException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=404,
            error_code="ERR_019",
            error_msg="ORDER NOT FOUND"
        )
        
class NotYourOrderException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=403,
            error_code="ERR_020",
            error_msg="NOT YOUR ORDER"
        )
        
class InvalidOrderStatusException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error_code="ERR_021",
            error_msg="INVALID ORDER STATUS"
        )