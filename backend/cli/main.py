import typer

import cli.ingestion as ingest
import cli.vector_db as vector_db

app = typer.Typer()
app.add_typer(ingest.app, name="ingest", help="Ingest databases.")
app.add_typer(vector_db.app, name="vdb", help="Commands related to the vector database.")

if __name__ == "__main__":
    app()
