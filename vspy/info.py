from typing import Dict, Iterator, Tuple

import requests

_DEFAULT_VERSIONS: Dict[str, str] = {
    "pytest": "6.0.2",
    "pytest-timeout": "1.4.2",
    "pylint": "2.6.0",
    "flake8": "3.8.3",
    "flake8-isort": "4.0.0",
    "mypy": "0.782",
    "black": "20.8b1",
    "tox": "3.20.0",
}

_INVALID_PROJECT_CHARS = {"<", ">", "\\", "/", ":", '"', "|", "?", "*"}


class Info:
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    """A class wrapper for project information"""

    def __init__(self, info_dict: Dict[str, str]) -> None:
        self.project: str = info_dict["project"]
        self.description: str = info_dict["description"]
        self.repository: str = info_dict["repository"]
        self.author: str = info_dict["author"]
        self.email: str = info_dict["email"]
        self.keywords: str = info_dict["keywords"]
        self.pytest: str = info_dict["pytest"]
        self.pytest_timeout: str = info_dict["pytest-timeout"]
        self.pylint: str = info_dict["pylint"]
        self.flake8: str = info_dict["flake8"]
        self.flake8_isort: str = info_dict["flake8-isort"]
        self.mypy: str = info_dict["mypy"]
        self.black: str = info_dict["black"]
        self.tox: str = info_dict["tox"]

    def get_dev_dependencies(self) -> Iterator[Tuple[str, str]]:
        """Yield all dev dependecies."""
        yield ("pytest", self.pytest)
        yield ("pytest-timeout", self.pytest_timeout)
        yield ("pylint", self.pylint)
        yield ("flake8", self.flake8)
        yield ("flake8-isort", self.flake8_isort)
        yield ("mypy", self.mypy)
        yield ("black", self.black)
        yield ("tox", self.tox)


def get_version(pck: str, df_v: str) -> str:
    """Get the current version for a provided package. If that fails, a default
    version is returned."""
    try:
        req = requests.get(f"https://pypi.org/pypi/{pck}/json")
        req.raise_for_status()
        version: str = req.json()["info"]["version"]
        return version
    except (ValueError, requests.exceptions.RequestException, KeyError):
        return df_v


def get_versions() -> Dict[str, str]:
    """Get current (or default in case fetching fails) versions for all dependencies."""
    return {pck: get_version(pck, df_v) for pck, df_v in _DEFAULT_VERSIONS.items()}


def prompt(msg: str) -> str:
    """Promt message and read input."""
    print(f"{msg}:", end=" ", flush=True)
    return input().strip()


def is_valid_project(project: str) -> bool:
    """Validate project name."""
    return bool(project) and not set(project).intersection(_INVALID_PROJECT_CHARS)


def get_info() -> Info:
    """Gather info needed to create project."""
    print("Fetching latest versions for dev dependencies...", flush=True)
    info: Dict[str, str] = get_versions()
    while True:
        project = prompt("Enter project name")
        if is_valid_project(project):
            info["project"] = project
            break
        print("Project name must not be empty")
        print(f"Project name must not include: {' '.join(_INVALID_PROJECT_CHARS)}")
        print(f"{project} is not a valid project name")
    print("Remaining fields can be empty")
    info["description"] = prompt("Enter project description")
    info["repository"] = prompt("Enter repository")
    info["author"] = prompt("Enter author")
    info["email"] = prompt("Enter email")
    info["keywords"] = prompt("Enter keywords")
    return Info(info)
