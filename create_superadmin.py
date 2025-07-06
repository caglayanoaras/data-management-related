import typer
import os
from app.core.database import get_sync_session, init_db
from app.models import User, UserType
from app.dependencies.auth import get_password_hash
from sqlmodel import select

cli = typer.Typer()


@cli.command()
def create_superadmin(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    name: str = typer.Option(..., prompt=True),
    surname: str = typer.Option(..., prompt=True),
    title: str = typer.Option(..., prompt=True),
):   
    # username: str, email: str, password: str, name: str, surname: str, title: str):
    """Add a new SuperAdmin user."""
    init_db()  # ensure tables exist
    hashed = get_password_hash(password)

    with get_sync_session() as session: 
        existing_email = session.exec(select(User).where(User.email == email)).first()
        existing_username = session.exec(select(User).where(User.username == username)).first()
        if existing_username:
            typer.secho("A user with this username already exists.", fg=typer.colors.RED)
            return 
        elif existing_email:
            typer.secho("A user with this email already exists.", fg=typer.colors.RED)
            return
        default_iamge_path = os.path.join('default_profile_image.png')

        user = User(username=username, email=email, hashed_pw=hashed, usertype=UserType.superadmin, name=name, surname=surname, title=title, profile_image_path=default_iamge_path, created_by='root', last_modified_by='root')
        session.add(user)
        session.commit()
        typer.secho(f"SuperAdmin '{username}: {email}' created.", fg=typer.colors.GREEN)



if __name__ == "__main__":
    cli()