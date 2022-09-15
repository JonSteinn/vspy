import asyncio
import pathlib
from typing import Dict

import pytest
from pytest_httpx import HTTPXMock

from tests.testutils.helpers import (
    TempFile,
    compare_against_static,
    get_pypi_url_and_res,
    vers_gen,
)
from tests.testutils.mocks import MockArguments, py_partial_page
from vspy.core import App
from vspy.core.file_io import path_from_root, read_file, read_json_file
from vspy.core.utils import is_empty_folder


async def _mock_urls(httpx_mock: HTTPXMock) -> Dict[str, str]:
    httpx_mock.add_response(
        url="https://www.python.org/downloads/", content=py_partial_page
    )
    cfg_file = path_from_root("vspy", "resources", "data.json")
    cfg = await read_json_file(cfg_file)
    version_map = dict(zip(cfg["dev-dependencies"], vers_gen()))
    data = [get_pypi_url_and_res(*package) for package in version_map.items()]
    for url, res in data:
        httpx_mock.add_response(url=url, json=res)
    return version_map


def _assert_existence(p: pathlib.Path, *rel_fpath: str):
    return all(map(lambda z: p.joinpath(z).is_file(), rel_fpath))


async def _assert_github_deploy(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_github_test_and_lint(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_vscode_settings(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==vs_config==")


async def _assert_name_init(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==init==")


async def _assert_name_main(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_name_typed(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==empty==")


async def _assert_tests_init(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==empty==")


async def _assert_tests_placeholder(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_coveragerc(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_editorconfig(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==editor_config==")


async def _assert_flake8(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==flake8==")


async def _assert_gitattribute(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==gitattributes==")


async def _assert_gitignore(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==gitignore==")


async def _assert_isort(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_pre_commit_config(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==pre_commit==")


async def _assert_pylintrc(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_changelog(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==changelog==")


async def _assert_license(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return await compare_against_static(fpath, "==license==")


async def _assert_manifest(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_mypy(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_pyproject(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_readme(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_requirements_dev(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_requirements(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_setup(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _assert_tox(
    version_map: Dict[str, str], args: MockArguments, fpath: pathlib.Path
) -> bool:
    return True


async def _asserter(version_map: Dict[str, str], dir_: str, args: MockArguments):
    files = {
        ".github/deploy.yml": _assert_github_deploy,
        ".github/test_and_lint.yml": _assert_github_test_and_lint,
        ".vscode/settings.json": _assert_vscode_settings,
        f"{args.name}/__init__.py": _assert_name_init,
        f"{args.name}/main.py": _assert_name_main,
        f"{args.name}/py.typed": _assert_name_typed,
        "tests/__init__.py": _assert_tests_init,
        "tests/test_placeholder.py": _assert_tests_placeholder,
        ".coveragerc": _assert_coveragerc,
        ".editorconfig": _assert_editorconfig,
        ".flake8": _assert_flake8,
        ".gitattribute": _assert_gitattribute,
        ".gitignore": _assert_gitignore,
        ".isort.cfg": _assert_isort,
        ".pre-commit-config.yaml": _assert_pre_commit_config,
        ".pylintrc": _assert_pylintrc,
        "CHANGELOG.md": _assert_changelog,
        "LICENSE": _assert_license,
        "MANIFEST.in": _assert_manifest,
        "mypy.ini": _assert_mypy,
        "pyproject.toml": _assert_pyproject,
        "README.rst": _assert_readme,
        "requirements-dev.txt": _assert_requirements_dev,
        "requirements.txt": _assert_requirements,
        "setup.py": _assert_setup,
        "tox.ini": _assert_tox,
    }
    p = pathlib.Path(dir_)
    assert _assert_existence(p, *files.keys())
    checks = await asyncio.gather(
        *(
            async_fn(version_map, args, p.joinpath(rel_path))
            for rel_path, async_fn in files.items()
        )
    )
    assert all(checks)


@pytest.mark.asyncio
async def test_app(httpx_mock: HTTPXMock):
    version_map = await _mock_urls(httpx_mock)
    with TempFile(0) as (dir_, _):
        args = MockArguments(
            dir_,
            "mylib",
            description="test-description",
            repository="test-repo",
            author="me",
            email="mine",
            keywords="test, example",
        )
        app = App(args, path_from_root("vspy", "resources", "data.json"))
        await app.start()
        await _asserter(version_map, dir_, args)
        app.cleanup()
        assert is_empty_folder(dir_)
