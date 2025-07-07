import typer

from app.ingestion.pipelines.manami_import_pipeline import import_manami_from_repo, import_manami_from_file

app = typer.Typer()


@app.command()
def from_repo():
    """Ingest manami (anime offline database) from their GitHub repository."""
    import_manami_from_repo()


@app.command()
def from_file(path: str = typer.Argument(..., help="JSON file path")):
    """Ingest manami (anime offline database) from a local file."""
    import_manami_from_file(path)
