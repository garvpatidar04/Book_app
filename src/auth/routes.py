from fastapi import APIRouter, status, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta

from .schemas import (
    UserCreateModel, 
    UserModel, 
    UserLoginModel, 
    UserBookModel, 
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel
)
from .utils import (
    create_access_token, 
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
    get_hashed_password
)
from .dependencies import (
    RefreshTokenBearer, 
    AccessTokenBearer, 
    get_current_user,
    RoleChecker
)
from src.errors import (
    InvalidCredentials,
    InvalidToken,
    UserAlreadyExists,
    UserNotFound,
    PasswordNotMatched
)
from .service import UserService
from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.mail import mail, create_message


user_routes = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 2

async def send_email(recipients: list[str], subject: str, body: str):
    """Send email asynchronously using background task"""
    message = create_message(recipients, subject, body)
    await mail.send_message(message)
    print("Email sent")


@user_routes.post(
        "/signup", 
        status_code=status.HTTP_201_CREATED
    )
async def create_user_account(
    user_data:UserCreateModel, 
    background_task: BackgroundTasks,
    session:AsyncSession = Depends(get_session)
    ):
    """
    Signup a new user
    Args:
        user_data: User data to create
    Returns:
        User object
    """
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise UserAlreadyExists()
    
    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email": email})

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h>Verify your email</h>
    <p>Please clink the <a href="{link}">link</a> to verify your email.</p>
    """
    background_task.add_task(
        send_email, [email], "Verify your Email", html_message
        )

    return {
        "message": "Account created, Check your Email to verify your account",
        "user": new_user
    }

@user_routes.get("/verify/{token}")
async def verify_user_account(token, session:AsyncSession = Depends(get_session)):
    """Verify the email"""
    data = decode_url_safe_token(token)
    user_email = data["email"]

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()
        
        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

@user_routes.post("/login")
async def login(user_login: UserLoginModel, session: AsyncSession = Depends(get_session)):
    """
    Authenticate a user
    Args:
        user_login: User login data
    Returns:
        Access token with additional data
    """
    email = user_login.email
    password = user_login.password
    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data = {"email": user.email, "user_uid":str(user.uid)}
            )
            refresh_token = create_access_token(
                user_data = {"email": user.email, "user_uid":str(user.uid)},
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "user_uid": str(user.uid)}
                }
            )
    
    raise InvalidCredentials()

@user_routes.get("/me", response_model=UserBookModel)
async def get_current_user(
    user = Depends(get_current_user), _: bool = Depends(role_checker) 
    ):
    return user

@user_routes.get("/logout")
async def logout(token_details: dict = Depends(AccessTokenBearer())):
    """
    Logout a user
    Args:
        token_details: Token details for logout
    Returns:
        Logout message
    """
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged out Successfully",},
        status_code=status.HTTP_200_OK
            )

@user_routes.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    """
    Refresh the access token
    Args:
        token_details: payload of refresh token
    Returns:
        Access token with additional data
    """
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(token_details['user'])
        return JSONResponse(content={"access_token": new_access_token})
    
    raise InvalidToken()

@user_routes.post("/password-reset-request")
async def password_reset_request(
    emails: PasswordResetRequestModel, 
    background_task: BackgroundTasks,
    ):
    """Password reset request"""
    email = emails.email
    token = create_url_safe_token({"email": email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"
    html_message = f"""
    <h>Reset Password</h>
    <p>Please click the <a href="{link}">link</a> to reset your password.</p>
    """

    background_task.add_task(
        send_email, [email], "Password Reset Request", html_message
        )
    
    return JSONResponse(
        content={"message": "Please check your email regarding password reset"},
        status_code=status.HTTP_200_OK
    )

@user_routes.post("/password-reset-confirm/{token}")
async def password_reset_confirmation(
    token: str, 
    passwords: PasswordResetConfirmModel,
    session:AsyncSession = Depends(get_session)
    ):
    """Confirm password reset"""
    new_password = passwords.new_password
    confirm_new_password = passwords.confirm_new_password

    if new_password != confirm_new_password:
        raise PasswordNotMatched()

    data = decode_url_safe_token(token)
    user_email = data["email"]

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if user is not None:
            hash_password = get_hashed_password(new_password)
            user_service.update_user(user, {"password_hash": hash_password}, session)

            return JSONResponse(
                content={"message": "Password reset successful"},
                status_code=status.HTTP_200_OK
            )
    
        return JSONResponse(
            content={"message": "Opps!... password not reset"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

@user_routes.post("/send_mail")
async def send_mail(emails: EmailModel, background_task: BackgroundTasks):
    """Send an email to a user"""

    emails = emails.addresses
    html = "<h>Welcome to the app.</h>"
    subject = "Welcome to our App"


    background_task.add_task(send_email, emails, subject, html)

    return {"message": "Email sent successfully"}

@user_routes.delete("/delete_me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user = Depends(get_current_user), session:AsyncSession = Depends(get_session)
    ):
    """Deletes a user"""
    email = user.email
    print("delete info")
    print(user)
    if email is None:
        raise UserNotFound()
    await user_service.delete_user(email, session)
    return {}