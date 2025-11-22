from wapang.common.exceptions import WapangException

class EmailAlreadyExistsException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409, 
            error_code="ERR_004", 
            error_msg="EMAIL ALREADY EXISTS"
        )
        
class InvalidFieldFormatException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=400, 
            error_code="ERR_003", 
            error_msg="INVALID FIELD FORMAT"
        )