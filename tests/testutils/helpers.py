from typing import Dict, Tuple


def get_pypi_url_and_res(
    package: str, version: str
) -> Tuple[str, Dict[str, Dict[str, str]]]:
    return f"https://pypi.org/pypi/{package}/json", {"info": {"version": version}}
