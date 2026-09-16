class JWTException(Exception):
    """Base class for JWT exceptions."""
    pass

class JWTDecodeError(JWTException):
    """Raised when there is an error decoding the JWT."""
    pass

class JWTExpiredError(JWTException):
    """Raised when the JWT has expired."""
    pass

class JWTInvalidTokenError(JWTException):
    """Raised when the JWT is invalid."""
    pass