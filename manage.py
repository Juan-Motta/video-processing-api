from datetime import datetime

import typer
import uvicorn

app = typer.Typer()


@app.command()
def hello(name: str):
    """
    Comando de prueba, imprime un saludo
    """
    print(f"Hello {name}")


@app.command()
def runserver():
    """
    Comando para correr el servidor de FastAPI con Uvicorn en el puerto 9000
    """
    uvicorn.run("src.main:app", host="0.0.0.0", port=9000, reload=True)


@app.command()
def makemigrations():
    """
    Comando para generar migraciones con Alembic
    """
    from subprocess import run

    run(
        [
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            f"""{datetime.now().strftime("%d_%m_%Y")}""",
        ],
        check=True,
    )


@app.command()
def migrate():
    """
    Comando para aplicar migraciones con Alembic
    """
    from subprocess import run

    run(["alembic", "upgrade", "head"], check=True)


@app.command()
def lint_black():
    """
    Comando para formatear el código con Black
    """
    from subprocess import run

    run(["black", "."], check=True)


@app.command()
def lint_isort():
    """
    Comando para ordenar las importaciones con isort
    """
    from subprocess import run

    run(["isort", "--profile", "black", "."], check=True)


@app.command()
def test():
    """
    Comando para correr las pruebas con pytest
    """
    from subprocess import run

    run(["pytest", "-vv"], check=True)


@app.command()
def coverage():
    """
    Comando para correr las pruebas con pytest y generar un reporte de cobertura
    """
    from subprocess import run

    run(["pytest", "--cov", "--cov-report=html"], check=True)


@app.command()
def lint():
    """
    Comando para correr los linters Black e isort
    """
    lint_black()
    lint_isort()


@app.command()
def export_requirements():
    """
    Comando para exportar las dependencias a requirements.txt
    """
    from subprocess import run

    run(
        [
            "poetry",
            "export",
            "-f",
            "requirements.txt",
            "--output",
            "requirements.txt",
            "--without-hashes",
        ],
        check=True,
    )


@app.command()
def runworker():
    """
    Comando para correr el worker de Celery
    """
    from subprocess import run

    run(
        [
            "poetry",
            "run",
            "celery",
            "--app=src.celery_worker.celery",
            "worker",
            "--concurrency=1",
            "--loglevel=DEBUG",
        ],
        check=True,
    )


@app.command()
def runpubsub():
    """
    Comando para correr el worker de Pub/Sub
    """
    from subprocess import run

    run(["poetry", "run", "python", "src/pubsub_worker.py"], check=True)


@app.command()
def generate_password(password: str):
    """
    Comando para generar un hash de contraseña
    """
    from src.apps.auth.utils import encrypt_password

    print(encrypt_password(password=password))


@app.command()
def run_locust():
    """
    Comando para correr Locust
    """
    from subprocess import run

    run(
        ["poetry", "run", "locust", "-f", "locust/main.py", "-P", "10000"],
        check=True,
    )


@app.command()
def pre_commit():
    """
    Comando para correr los hooks de pre-commit
    """
    from subprocess import run

    run(["pre-commit", "run", "--all-files"], check=True)


if __name__ == "__main__":
    app()
