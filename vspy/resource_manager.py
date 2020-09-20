import shutil
from pathlib import Path

_ROOT = Path(__file__).parent.joinpath("resources")


def copy_file(fname: str, path: Path) -> None:
    """Copy fname from resources to path."""
    shutil.copy(_ROOT.joinpath(fname), path.joinpath(fname))
