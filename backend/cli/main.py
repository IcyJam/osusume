import typer

import ingest

app = typer.Typer()
app.add_typer(ingest.app, name="ingest", help="Ingest manami (anime offline database)")

if __name__ == "__main__":
    app()
