class Error(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundError(Error):
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class DataValidationError(Error):
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class ServerError(Error):
    def __init__(self, message: str):
        super().__init__(message, status_code=503)
