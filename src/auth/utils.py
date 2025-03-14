from passlib.context import CryptContext
from fastapi import HTTPException
import jwt
import uuid
import logging
from datetime import datetime, timedelta
from src.config import Config
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

pass_context = CryptContext(
    schemes=["bcrypt"]
)

serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET,
    salt="email-configuration"
)

access_token_time = 3600  # 1 hour


def get_hashed_password(password: str) -> str:
    """
    Generate a hashed password using bcrypt.
    """
    hash = pass_context.hash(password)
    return hash

def verify_password(password: str, hash: str) -> bool:
    """
    Verify a password using bcrypt.
    Returns True if the password matches the hashed password, False otherwise.
    """
    return pass_context.verify(password, hash)


def create_access_token(user_data, expiry: timedelta = None, refresh: bool = False) -> str:
    """
    Create a JWT token for the user
    """
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry is not None else timedelta(seconds=access_token_time)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    """
    Decode a JWT token and return its payload
    """
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
            )
        return token_data
    except jwt.PyJWTError as jwte:
        logging.exception(jwte)
        return None
    except Exception as e:
        logging.exception(e)
        return None
    
def create_url_safe_token(data: dict, expiry: timedelta = None):

    token = serializer.dumps(data)

    return token

def decode_url_safe_token(token:str):
    try:
        token_data = serializer.loads(token)

        return token_data
    
    except Exception as e:
        logging.error(str(e))