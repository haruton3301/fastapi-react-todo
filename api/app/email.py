from fastapi_mail import FastMail, MessageSchema, MessageType, ConnectionConfig

from app.config import settings


def _make_conf() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME="",
        MAIL_PASSWORD="",
        MAIL_FROM=settings.smtp_from,
        MAIL_PORT=settings.smtp_port,
        MAIL_SERVER=settings.smtp_host,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=False,
        VALIDATE_CERTS=False,
    )


async def send_password_reset_email(to: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    message = MessageSchema(
        subject="パスワードリセット",
        recipients=[to],
        body=f"以下のURLからパスワードをリセットしてください（有効期限1時間）:\n\n{reset_url}",
        subtype=MessageType.plain,
    )
    await FastMail(_make_conf()).send_message(message)
