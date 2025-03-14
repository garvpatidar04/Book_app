from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status
from sqlalchemy.exc import SQLAlchemyError
import asyncio

class BooklyException(Exception):
    """This is the base class for all bookly errors"""
    pass

class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is needed"""
    pass

class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is needed"""
    pass

class UserAlreadyExists(BooklyException):
    """User has provided an email for a user who exists during sign up."""
    pass

class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during log in."""
    pass

class InsufficientPermission(BooklyException):
    """User does not have the necessary permissions to perform an action."""
    pass

class BookNotFound(BooklyException):
    """Book Not found"""
    pass

class ReviewNotFound(BooklyException):
    """Book Not found"""
    pass

class TagNotFound(BooklyException):
    """Tag Not found"""
    pass

class TagAlreadyExists(BooklyException):
    """Tag already exists"""
    pass

class UserNotFound(BooklyException):
    """User Not found"""
    pass

class AccountNotVerified(Exception):
    """Account not yet verified"""
    pass

class PasswordNotMatched(Exception):
    """passwords did not matched"""
    pass

def create_exception_handler(
        status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    
    async def exception_handler(request: Request, exc: Exception):
        
        return JSONResponse(status_code=status_code, content=initial_detail)
    
    return exception_handler

def register_error_handler(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists"
            },
        ),
    )

    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found"
            },
        ),
    )

    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found"
            },
        ),
    )

    app.add_exception_handler(
        ReviewNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Review not found",
                "error_code": "review_not_found"
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid email or password",
                "error_code": "Invalid_email_or_password"
            },
        ),
    )

    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token or revoked",
                "resolution": "Get a new Token or renew it",
                "error_code": "invalid_token"
            },
        ),
    )

    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid token or revoked",
                "resolution": "Get a new Token or renew it",
                "error_code": "token_revoked"
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "valid access token is required",
                "resolution": "please provide a valid access token",
                "error_code": "access_token_required"
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "valid refresh token is required",
                "resolution": "please provide a valid refresh token",
                "error_code": "refresh_token_required"
            },
        ),
    )

    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "You do not have sufficient permissions to perform this action",
                "error_code": "insufficient_permission"
            },
        ),
    )

    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "tag_not_found"
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Tag already exists",
                "error_code": "tag_already_exists"
            },
        ),
    )

    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "account not verified",
                "error_code": "account_not_verified",
                "resolution": "Please check you email, to verify your account first."
            },
        ),
    )

    app.add_exception_handler(
        PasswordNotMatched,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Password do not match",
                "error_code": "password_not_reset",
                "resolution": "Please enter both the password same."
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):

        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        print(str(exc))
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )