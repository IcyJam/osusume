import typer

from cli.vector_db import initialize_collection

app = typer.Typer()
app.add_typer(initialize_collection.app, name="init")