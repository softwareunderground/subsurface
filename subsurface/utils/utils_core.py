from pathlib import Path


def get_extension(path):
    p = Path(path)
    return p.suffix