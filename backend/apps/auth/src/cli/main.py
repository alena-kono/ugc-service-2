import asyncio
from typing import Annotated

import pydantic
import typer
from src.auth import dependencies as auth_depends
from src.auth.exceptions import UserUsernameExistsError
from src.cli import messages as msg
from src.cli.superuser import create_user_with_internal_permissions

app = typer.Typer(name="Create superuser with all permissions granted")


@app.command()
def create_superuser(
    username: Annotated[str, typer.Option()],
    first_name: Annotated[str, typer.Option()],
    last_name: Annotated[str, typer.Option()],
) -> None:
    password = typer.prompt(msg.ENTER_PASSWORD, hide_input=True)
    confirmed_password = typer.prompt(msg.CONFIRM_PASSWORD, hide_input=True)

    if not password == confirmed_password:
        typer.echo(msg.PASSWORDS_DO_NOT_MATCH, err=True)
        raise typer.Exit(code=1)
    try:
        validated_user = auth_depends.UserSignUp(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=confirmed_password,
        )
    except pydantic.ValidationError as err:
        typer.echo(err, err=True)
        raise typer.Exit(code=1)

    try:
        created_user, created_permissions_names = asyncio.run(
            create_user_with_internal_permissions(user=validated_user)
        )
    except UserUsernameExistsError:
        aborting_msg = typer.style(msg.ABORTING, fg=typer.colors.RED, bold=True)
        user_exists_msg = typer.style(msg.USERNAME_ALREADY_EXISTS, fg=typer.colors.RED)

        typer.echo(
            user_exists_msg.format(username=validated_user.username),
            err=True,
        )
        typer.echo(aborting_msg, err=True)
        raise typer.Exit(code=1)

    success_msg = typer.style(msg.SUPERUSER_CREATED, fg=typer.colors.GREEN, bold=True)
    success_permissions_msg = typer.style(
        msg.PERMISSIONS_CREATED, fg=typer.colors.GREEN, bold=True
    )
    typer.echo(
        success_msg.format(
            user_data=created_user.dict(exclude={"password", "permissions"})
        ),
    )
    typer.echo(success_permissions_msg.format(permissions=created_permissions_names))


def main() -> None:
    app()
