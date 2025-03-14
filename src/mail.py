from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from src.config import Config
from pathlib import Path
from typing import List

BaseDir = Path(__file__).resolve().parent

# config for mail 
mail_config = ConnectionConfig(
    MAIL_USERNAME = Config.MAIL_USERNAME,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_FROM_NAME = Config.MAIL_FROM_NAME,
    MAIL_SSL_TLS = False,
    MAIL_STARTTLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

mail = FastMail(mail_config)

def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=MessageType.html
    )
    return message