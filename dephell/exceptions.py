

class ExtraException(Exception):
    def __init__(self, message: str = None, **kwargs):
        if message:
            self.message = message
        self.extra = kwargs
        super().__init__(message, kwargs)

    def __str__(self) -> str:
        return self.message


class PackageNotFoundError(ExtraException, LookupError):
    message = 'package not found'


class InvalidFieldsError(ExtraException, ValueError):
    message = 'invalid fields'
