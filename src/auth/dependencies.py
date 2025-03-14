from typing import List, Any

from fastapi.security import HTTPBearer
from fastapi import status, Request, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio.session import AsyncSession

from src.db.redis import token_in_blocklist
from src.db.main import get_session 
from src.db.models import User

from .utils import decode_token
from . service import UserService

from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified
)

user_service = UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = decode_token(token)

        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()

        if not self.token_valid(token):
            raise InvalidToken()

        return token_data
            

    def token_valid(self, token: str) -> bool:

        token_data = decode_token(token)

        return token_data is not None
    
    def verify_token_data(self, token_data):
        raise NotImplementedError("Implemented this in child class")
    

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        """
        It checks that the token is access token is not then raise an Exception"""
        if token_data and token_data['refresh']:
            raise AccessTokenRequired()
        

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        """
        It checks that the token is refresh token is not then raise an Exception"""
        if token_data and not token_data['refresh']:
            raise RefreshTokenRequired()
        

async def get_current_user(
        token_details: dict = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session)
        ):
    """
    Retrieve current user from token details"""
    email = token_details['user']['email']

    user = await user_service.get_user_by_email(email, session)

    return user


class RoleChecker:
    def __init__(self, access_roles: List[str]) -> None:
        self.access_roles = access_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.access_roles:
            return True
        
        raise InsufficientPermission()
