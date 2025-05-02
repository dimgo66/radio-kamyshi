import logging
from typing import Any, Dict, Optional

from emails.message import Message
from fastapi import BackgroundTasks

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    background_tasks: BackgroundTasks,
    subject: str,
    html_content: str,
    to_email: str,
) -> None:
    """
    Отправка email в фоновом режиме.
    """
    background_tasks.add_task(
        _send_email,
        subject=subject,
        html_content=html_content,
        to_email=to_email,
    )


def _send_email(
    subject: str,
    html_content: str,
    to_email: str,
) -> None:
    """
    Отправка email через SMTP сервер.
    В реальности здесь будет настройка SMTP.
    """
    # Заглушка для демонстрации
    logger.info(f"Sending email to {to_email}: {subject}")
    
    # В реальном проекте нужно настроить SMTP-сервер
    # message = Message(
    #     subject=subject,
    #     html=html_content,
    #     mail_from=(settings.EMAIL_FROM_NAME, settings.EMAIL_FROM)
    # )
    # smtp = message.send(
    #     to=(to_email,),
    #     smtp={
    #         "host": settings.SMTP_HOST,
    #         "port": settings.SMTP_PORT,
    #         "user": settings.SMTP_USER,
    #         "password": settings.SMTP_PASSWORD,
    #         "tls": settings.SMTP_TLS,
    #     }
    # )
    
    logger.info(f"Email to {to_email} sent successfully") 