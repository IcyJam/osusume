import typer

from cli.ingestion import manami

app = typer.Typer()
app.add_typer(manami.app, name="manami")
