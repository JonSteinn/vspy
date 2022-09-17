import asyncio
import pathlib
from typing import Tuple

import pytest
from pytest_httpx import HTTPXMock

from tests.testutils.helpers import TempFile, compare_against_static, mock_urls
from tests.testutils.mocks import MockArguments
from vspy.core import App
from vspy.core.file_io import path_from_root, read_file
from vspy.core.utils import is_empty_folder


def _assert_existence(p: pathlib.Path, *rel_fpath: str):
    return all(map(lambda z: p.joinpath(z).is_file(), rel_fpath))


async def _assert_github_deploy(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = """name: build-and-deploy

on:
  push:
    branches:
      - master

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.10
    - name: install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install setuptools wheel twine
    - name: build
      run: python setup.py sdist
    - name: deploy
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: twine upload dist/*
"""
    return got, expected


async def _assert_github_test_and_lint(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = """name: tests

on: [push, pull_request]

jobs:

  test:
    strategy:
      fail-fast: false
      matrix:
        include:
          - python: '3.10'
            toxenv: flake8
            os: ubuntu-latest
          - python: '3.10'
            toxenv: mypy
            os: ubuntu-latest
          - python: '3.10'
            toxenv: pylint
            os: ubuntu-latest
          - python: '3.10'
            toxenv: black
            os: ubuntu-latest
          - python: '3.10'
            toxenv: py310
            os: macos-latest
          - python: '3.10'
            toxenv: py310
            os: windows-latest
          - python: '3.7'
            toxenv: py37
            os: ubuntu-latest
          - python: '3.8'
            toxenv: py38
            os: ubuntu-latest
          - python: '3.9'
            toxenv: py39
            os: ubuntu-latest
          - python: '3.10'
            toxenv: py310
            os: ubuntu-latest

    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python }}
      - name: install dependencies
        run: python -m pip install --upgrade pip tox
      - name: run
        env:
          TOXENV: ${{ matrix.toxenv }}
        run: tox
      - name: setup
        run: python setup.py install
"""
    return got, expected


async def _assert_vscode_settings(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==vs_config==")


async def _assert_name_init(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==init==")


async def _assert_name_main(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==main==")


async def _assert_name_typed(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==empty==")


async def _assert_tests_init(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==empty==")


async def _assert_tests_placeholder(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""from {args.name} import __version__


def test_placeholder():
    assert __version__ == "0.0.1"
"""
    return got, expected


async def _assert_coveragerc(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""[run]
branch = True
omit =
    tests/*
    {args.name}/main.py

[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover

    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug

    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError

    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:

    # Don't complain about abstract methods, they aren't run:
    @(abc\.)?abstractmethod

    # Don't complain about type imports
    if TYPE_CHECKING:

ignore_errors = True
"""
    return got, expected


async def _assert_editorconfig(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==editor_config==")


async def _assert_flake8(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==flake8==")


async def _assert_gitattribute(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==gitattributes==")


async def _assert_gitignore(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==gitignore==")


async def _assert_isort(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""[settings]
known_first_party={args.name}
default_section=THIRDPARTY
multi_line_output=3
include_trailing_comma=True
force_grid_wrap=0
use_parentheses=True
line_length=88
"""
    return got, expected


async def _assert_pre_commit_config(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==pre_commit==")


async def _assert_pylintrc(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""[MASTER]
ignore-patterns=test_.*?py
ignore= tests
init-hook="from pylint.config import find_pylintrc; import os, sys; sys.path.append(os.path.dirname(find_pylintrc())+'/{args.name}')"
disable=missing-module-docstring,
        fixme
good-names=_

[SIMILARITIES]
ignore-imports=yes
"""
    return got, expected


async def _assert_changelog(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==changelog==")


async def _assert_license(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==license==")


async def _assert_manifest(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""include {args.name}/py.typed
include requirements.txt
"""
    return got, expected


async def _assert_mypy(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""[mypy]
strict = True
pretty = True
check_untyped_defs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
disallow_untyped_decorators = True
disallow_any_unimported = True
warn_return_any = True
warn_unused_ignores = True
warn_unused_configs = True
no_implicit_optional = True
show_error_codes = True
show_traceback = True
files = {args.name}/**/*.py

[{args.name}-tests.*]
ignore_errors = True
"""
    return got, expected


async def _assert_pyproject(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = """[tool.black]
target-version = ['py310']
include = '\.pyi?$'
exclude = '''
(
  /(
      \.eggs         # exclude a few common directories in the
    | \.git          # root of the project
    | \.hg
    | \.mypy_cache
    | \.tox
    | \.venv
    | _build
    | buck-out
    | build
    | dist
  )/
)
'''
"""
    return got, expected


async def _assert_readme(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""****
{args.name}
****

subtitle
########

subsubtitle
**********************
"""
    return got, expected


async def _assert_requirements_dev(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = "\n".join(f"{k}=={v}" for k, v in args.dev_packages.items()) + "\n"
    return got, expected


async def _assert_requirements(
    args: MockArguments, fpath: pathlib.Path
) -> Tuple[str, str]:
    return await compare_against_static(fpath, "==empty==")


async def _assert_setup(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""#!/usr/bin/env python
import os
import sys

from setuptools import find_packages, setup

_MIN_PY_VERSION = (3, 7)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


def get_version():
    with open("{args.name}/__init__.py", encoding="utf-8") as init_file:
        for line in init_file.readlines():
            if line.startswith("__version__"):
                return line.split(" = ")[1].rstrip()[1:-1]
    raise ValueError("Version not found in name/__init__.py")


def check_min_py_version():
    if sys.version_info[:2] < _MIN_PY_VERSION:
        raise RuntimeError(
            f"Python version >= {{'.'.join(map(str, _MIN_PY_VERSION))}} required."
        )


def main():
    check_min_py_version()
    setup(
        name="{args.name}",
        version=get_version(),
        author="{args.author}",
        author_email="{args.email}",
        description="{args.description}",
        license="GPLv3",
        keywords="{args.keywords}",
        url="{args.repository}",
        project_urls={{
            "Source": "{args.repository}",
            "Tracker": "{args.repository}/issues",
        }},
        packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
        package_data={{"{args.name}": ["py.typed"]}},
        include_package_data=True,
        long_description_content_type="text/x-rst",
        long_description=read("README.rst"),
        install_requires=read("requirements.txt").splitlines(),
        python_requires=">=3.7",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: Implementation :: CPython",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Development Status :: 3 - Alpha",
        ],
        entry_points={{"console_scripts": ["{args.name}={args.name}.main:main"]}},
    )


if __name__ == "__main__":
    main()
"""
    return got, expected


async def _assert_tox(args: MockArguments, fpath: pathlib.Path) -> Tuple[str, str]:
    got = await read_file(fpath)
    expected = f"""[tox]
minversion = {args.dev_packages['tox']}
envlist =
    flake8, mypy, pylint, black
    py{{37,38,39,310}},

[default]
basepython=python3.10

[testenv]
description = run test
basepython =
    py37: python3.7
    py38: python3.8
    py39: python3.9
    py310: python3.10
deps = -rrequirements-dev.txt
commands = pytest

[pytest]
addopts = --doctest-modules --doctest-ignore-import-errors
testpaths = tests {args.name} README.rst
markers = slow: marks tests as slow (deselect with '-m "not slow"')

[testenv:flake8]
description = run flake8 (linter)
basepython = {{[default]basepython}}
skip_install = True
deps = -rrequirements-dev.txt
commands =
    flake8 --isort-show-traceback {args.name}

[testenv:pylint]
description = run pylint (static code analysis)
basepython = {{[default]basepython}}
deps = -rrequirements-dev.txt
commands = pylint {args.name}

[testenv:mypy]
description = run mypy (static type checker)
basepython = {{[default]basepython}}
deps = -rrequirements-dev.txt
commands = mypy

[testenv:black]
description = check that comply with autoformating
basepython = {{[default]basepython}}
deps = -rrequirements-dev.txt
commands = black --check --diff .
"""
    return got, expected


async def _asserter(dir_: str, args: MockArguments):
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
        *(async_fn(args, p.joinpath(rel_path)) for rel_path, async_fn in files.items())
    )
    for key, (got, expected) in zip(files.keys(), checks):
        assert got == expected, key
    assert all(checks)


@pytest.mark.asyncio
async def test_app(httpx_mock: HTTPXMock):
    version_map = await mock_urls(httpx_mock)
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
        args.py_versions = app._project._args["py_versions"]
        args.dev_packages = app._project._args["dependencies"]
        for k1, k2 in zip(sorted(version_map), sorted(args.dev_packages)):
            assert k1 == k2 and version_map[k1] == args.dev_packages[k2]
        assert tuple(args.py_versions) == ("3.7", "3.8", "3.9", "3.10")
        assert len(version_map) == len(args.dev_packages)
        await _asserter(dir_, args)
        app.cleanup()
        assert is_empty_folder(dir_)
