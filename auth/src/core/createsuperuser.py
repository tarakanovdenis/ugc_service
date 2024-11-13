import re
from asyncio import run as aiorun

import typer
from rich import print
from src.models.user import User

from src.db.postgres import db_helper


# Regular expression for validating an Email
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


async def createsuperuser():
    username = typer.prompt(
        'Username (leave blank to use "admin")',
        default='admin',
        show_default=False
    )
    if not username:
        username = 'admin'

    first_name = typer.prompt('First name')
    last_name = typer.prompt('Last name')

    while True:
        email = typer.prompt('Email address')
        if re.fullmatch(regex, email):
            break
        else:
            print('[bold red]Error: Your email is invalid.[bold red]')

    while True:
        password = typer.prompt('Password')
        repeat_password = typer.prompt('Password (again)')
        if password == repeat_password:
            break
        else:
            print('[bold red]Error: Your passwords didn\'t match.[bold red]')

    superuser = User(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_superuser=True,
        is_staff=True,
    )

    async with db_helper.async_session() as session:
        try:
            session.add(superuser)
            await session.commit()
            await session.refresh(superuser)
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def main():
    aiorun(createsuperuser())


if __name__ == '__main__':
    typer.run(main)
