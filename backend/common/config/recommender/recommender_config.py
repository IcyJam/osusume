from pathlib import Path

import yaml
from openai import BaseModel


class RecommenderConfiguration(BaseModel):
    embedder: str
    dimensions: int
    prompt_id: str
    top_k: int
    n_selected: int


def load_recommender_config(path: str | Path) -> RecommenderConfiguration:
    """
    Load a RecommenderConfiguration from a YAML file.

    :param path: Path to the YAML config file.
    :type path: Path or str.
    :return: Parsed RecommenderConfiguration instance.
    :rtype: RecommenderConfiguration
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return RecommenderConfiguration(**data)


def get_recommender_config():
    return load_recommender_config("common/config/recommender/pipeline_config.yaml")
