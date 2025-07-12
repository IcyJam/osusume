import typer

import cli.ingestion as ingest

app = typer.Typer()
app.add_typer(ingest.app, name="ingest", help="Ingest databases.")

if __name__ == "__main__":
    app()
