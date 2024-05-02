from pathlib import Path


def get_extension(path):
    try:
        p = Path(path)
        return p.suffix
    except TypeError:
        return False