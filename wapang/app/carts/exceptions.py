from wapang.common.exceptions import WapangException

class MissingRequiredFieldsException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=400,
            error_code="ERR_001",
            error_msg="MISSING REQUIRED FIELDS"
        )
        
class InvalidFieldFormatException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=400,
            error_code="ERR_002",
            error_msg="INVALID FIELD FORMAT"
        )
        
class UnauthenticatedException(WapangException):
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
            error_code="ERR_024",
            error_msg="EMPTY ITEM LIST"
        )