import typer

from cli.ingestion import manami, mangaupdates

app = typer.Typer()
app.add_typer(manami.app, name="manami")
app.add_typer(mangaupdates.app, name="mangaupdates")
