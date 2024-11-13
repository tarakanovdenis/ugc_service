from pathlib import Path
import smtplib
from email.message import EmailMessage
# from email.mime.text import MIMEText
# from getpass import getpass

from jinja2 import Environment, FileSystemLoader
from redis import Redis

from core.config import settings
from utils.messages import messages
from utils.queries import get_users
from utils import helpers

import aiosmtplib


async def get_yandex_smtp_server():
    server = aiosmtplib.SMTP(
        hostname=settings.yandex_smtp_host,
        port=settings.yandex_smtp_port,
    )
    await server.connect()
    await server.login(
        settings.yandex_login,
        settings.yandex_password
    )
    return server


async def get_google_smtp_server():
    server = aiosmtplib.SMTP(
        hostname=settings.gmail_smtp_host,
        port=settings.gmail_smtp_port,
        start_tls=False,
        use_tls=False,
    )
    await server.connect()
    await server.starttls()
    await server.login(
        settings.gmail_login,
        settings.gmail_password
    )
    return server


async def send_html_template_email(
    subject: str,
    receiver_address: str | list[str],
    path_to_template: str,
    data: dict,
    sender_address: str = settings.sender_address,
    many_receivers: bool = False,
):
    message = EmailMessage()

    message["Subject"] = subject
    message["From"] = sender_address
    message["To"] = receiver_address

    current_path = Path(__name__).parent.parent
    loader = FileSystemLoader(current_path)
    env = Environment(loader=loader)

    template = env.get_template(path_to_template)
    rendered_template = template.render(**data)
    message.add_alternative(rendered_template, subtype="html")

    sender_address_domain = sender_address.split("@")[1]

    if sender_address_domain == settings.yandex_domain:
        server = await get_yandex_smtp_server()

    elif sender_address_domain == settings.gmail_domain:
        server = await get_google_smtp_server()

    if many_receivers:
        count_sent_messages = 0
        try:
            for receiver_email in receiver_address:
                message = EmailMessage()

                message['From'] = sender_address
                message['To'] = receiver_email
                message['Subject'] = subject

                message.add_alternative(rendered_template, subtype='html')

                try:
                    await server.sendmail(sender_address, receiver_email, message.as_string())
                except aiosmtplib.SMTPException as exc:
                    reason = f'{type(exc).__name__}: {exc}'
                    print(
                        f'The message was not sent to the user: {receiver_email}.'
                        f'Reason: {reason}')
                else:
                    count_sent_messages += 1
        finally:
            await server.quit()
            print(f'{count_sent_messages} messages were sent successfully.')
    else:
        try:
            await server.sendmail(
                sender_address,
                receiver_address,
                message.as_string(),
            )
        except aiosmtplib.SMTPException as exc:
            reason = f"{type(exc).__name__}: {exc}"
            print(f"The message was not sent. The reason:\n{reason}")
            return {
                "detail": messages.UNSUCCESSFULL_SENDING_RESET_PASSWORD_TOKEN_EMAIL
            }
        else:
            return {
                "detail": messages.SUCCESSFULLY_SENDING_RESET_PASSWORD_TOKEN_EMAIL
            }
        finally:
            await server.quit()


async def send_welcome_notification(
    rabbitmq_message: dict[str, str]
):
    subject = 'Welcome to Friday Cinema ❤️‍🔥'

    receiver_address = rabbitmq_message['email']
    sender_address = settings.sender_address
    path_to_template = './static/templates/welcome_email.html'
    first_name = rabbitmq_message["first_name"]
    last_name = rabbitmq_message["last_name"]
    username = rabbitmq_message["username"]

    data = {
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': receiver_address,
    }

    return await send_html_template_email(
        subject,
        receiver_address,
        path_to_template,
        data,
        sender_address=sender_address,
    )


async def send_new_film_notification_by_email(
    redis: Redis,
    rabbitmq_message: dict[str: str]
):
    subject = 'Try the novelty in Friday Cinema 📽️👏'

    receiver_addressess = helpers.get_user_email_list_from_cache(redis)

    if not receiver_addressess:
        users_orm = get_users()
        users_dto = helpers.convert_user_orm_to_user_dto(users_orm)
        receiver_addressess = helpers.get_email_user_list(users_dto)
        helpers.put_user_email_list_to_cache(redis, receiver_addressess)

    sender_address = settings.sender_address
    path_to_template = './static/templates/new_film.html'
    data = {
        'title': rabbitmq_message['title'],
        'description': rabbitmq_message['description']
    }

    return await send_html_template_email(
        subject,
        receiver_addressess,
        path_to_template,
        data,
        sender_address,
    )


async def send_reset_password_token_email(
    rabbitmq_message: dict[str, str]
):
    subject = "Password reset 👀"
    receiver_address = rabbitmq_message["email"]
    sender_address = settings.sender_address
    path_to_template = "./static/templates/password_reset_email.html"
    reset_password_token = rabbitmq_message["reset_password_token"]
    username = rabbitmq_message["username"]
    first_name = rabbitmq_message["first_name"]
    last_name = rabbitmq_message["last_name"]

    data = {
        "domain_name": settings.auth_service_domain_name,
        "reset_password_token": reset_password_token,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }

    return await send_html_template_email(
        subject,
        receiver_address,
        path_to_template,
        data,
        sender_address=sender_address
    )
