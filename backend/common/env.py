from pathlib import Path
from dotenv import load_dotenv
import os


def find_project_root(marker=".env") -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    raise FileNotFoundError(f"Could not find {marker} in any parent directories.")


project_root = find_project_root()
load_dotenv(dotenv_path=project_root / ".env")


def get_env_variable(var_name: str) -> str:
    return os.getenv(var_name)
