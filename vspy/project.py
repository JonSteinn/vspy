from pathlib import Path
from typing import Iterator, Tuple

from .info import Info
from .resource_manager import copy_file


def create_project(info: Info) -> None:
    """Create the project."""
    print(f"Creating project in {Path.cwd().absolute().as_posix()}")
    _create_src(info.project)
    _create_tests(info.project)
    _create_vscode()
    _create_github()
    _create_editorconfig()
    _create_flake8()
    _create_gitattributes()
    _create_gitignore()
    _create_isort(info.project)
    _create_precommit()
    _create_pylintrc(info.project)
    _create_changelog()
    _create_license()
    _create_manifest(info.project)
    _create_mypy(info.project)
    _create_pyprojecttoml()
    _create_readme(info.project)
    _create_reqdev(info.get_dev_dependencies())
    _create_setup(info)
    _create_tox(info)


def _create_src(name: str) -> None:
    project_dir = Path.cwd().joinpath(name)
    project_dir.mkdir(exist_ok=True)
    with project_dir.joinpath("__init__.py").open("w") as f:
        f.write('__version__ = "0.0.1"\n')
    project_dir.joinpath("py.typed").touch()
    copy_file("main.py", project_dir)


def _create_tests(name: str) -> None:
    test_dir = Path.cwd().joinpath("tests")
    test_dir.mkdir(exist_ok=True)
    test_dir.joinpath("__init__.py").touch()
    with test_dir.joinpath("test_placeholder.py").open("w") as f:
        f.write(f"from {name} import __version__\n\n\ndef test_placeholder():")
        f.write('    assert __version__ == "0.0.1"\n')


def _create_vscode() -> None:
    vs_dir = Path.cwd().joinpath(".vscode")
    vs_dir.mkdir(exist_ok=True)
    copy_file("settings.json", vs_dir)


def _create_github() -> None:
    github_dir = Path.cwd().joinpath(".github")
    github_dir.mkdir(exist_ok=True)
    workflow_dir = github_dir.joinpath("workflows")
    workflow_dir.mkdir(exist_ok=True)
    copy_file("test.yml", workflow_dir)


def _create_editorconfig() -> None:
    copy_file(".editorconfig", Path.cwd())


def _create_flake8() -> None:
    copy_file(".flake8", Path.cwd())


def _create_gitattributes() -> None:
    copy_file(".gitattribute", Path.cwd())


def _create_gitignore() -> None:
    copy_file(".gitignore", Path.cwd())


def _create_isort(name: str) -> None:
    with Path.cwd().joinpath(".isort.cfg").open("w") as f:
        f.write("[settings]\n")
        f.write(f"known_first_party = {name}\n")
        f.write("default_section = THIRDPARTY\n")
        f.write("multi_line_output=3\n")
        f.write("include_trailing_comma=True\n")
        f.write("force_grid_wrap=0\n")
        f.write("use_parentheses=True\n")
        f.write("line_length=88\n")


def _create_precommit() -> None:
    copy_file(".pre-commit-config.yaml", Path.cwd())


def _create_pylintrc(name: str) -> None:
    hook = (
        'init-hook="from pylint.config import find_pylintrc; import os, sys; '
        f"sys.path.append(os.path.dirname(find_pylintrc())+'/{name}')\"\n"
    )
    with Path.cwd().joinpath(".pylintrc").open("w") as f:
        f.write("[MASTER]\n")
        f.write("ignore-patterns=test_.*?py\n")
        f.write("ignore=tests\n")
        f.write(hook)
        f.write("disable=bad-continuation,\n")
        f.write("        missing-module-docstring,\n")
        f.write("        fixme\n")
        f.write("good-names=i,j,n,k,x,y,f,_\n\n")
        f.write("[SIMILARITIES]\n")
        f.write("ignore-imports=yes\n")


def _create_changelog() -> None:
    copy_file("CHANGELOG.md", Path.cwd())


def _create_license() -> None:
    copy_file("LICENSE", Path.cwd())


def _create_manifest(name: str):
    with Path.cwd().joinpath("MANIFEST.in").open("w") as f:
        f.write(f"include {name}/py.typed\n")


def _create_mypy(name: str) -> None:
    with Path.cwd().joinpath("mypy.ini").open("w") as f:
        f.write("[mypy]\n")
        f.write("warn_return_any = True\n")
        f.write("warn_unused_configs = True\n")
        f.write(f"files = {name}/**/*.py\n")


def _create_pyprojecttoml() -> None:
    copy_file("pyproject.toml", Path.cwd())


def _create_readme(name: str) -> None:
    with Path.cwd().joinpath("README.rst").open("w") as f:
        f.write(f"{'*' * len(name)}\n")
        f.write(f"{name}\n")
        f.write(f"{'*' * len(name)}\n")
        f.write("\n")
        f.write("subtitle\n")
        f.write("########\n")
        f.write("\n")
        f.write("subsubtitle\n")
        f.write("**********************\n")


def _create_reqdev(dev_deps: Iterator[Tuple[str, str]]) -> None:
    with Path.cwd().joinpath("requirements-dev.txt").open("w") as f:
        for pck, ver in dev_deps:
            f.write(f"{pck}>={ver}\n")


def _create_setup(info: Info) -> None:
    # pylint: disable=too-many-statements
    with Path.cwd().joinpath("setup.py").open("w") as f:
        f.write("#!/usr/bin/env python\n")
        f.write("import os\n")
        f.write("\n")
        f.write("from setuptools import find_packages, setup\n")
        f.write("\n")
        f.write("\n")
        f.write("def read(fname):\n")
        f.write(
            (
                "    return open(os.path.join(os.path.dirname(__file__), fname), "
                'encoding="utf-8").read()\n'
            )
        )
        f.write("\n")
        f.write("\n")
        f.write("def get_version():\n")
        f.write(
            (
                f'    with open("{info.project}/__init__.py", '
                'encoding="utf-8") as init_file:\n'
            )
        )
        f.write("        for line in init_file.readlines():\n")
        f.write('            if line.startswith("__version__"):\n')
        f.write('                return line.split(" = ")[1].rstrip()[1:-1]\n')
        f.write(
            f'    raise ValueError("Version not found in {info.project}/__init__.py")\n'
        )
        f.write("\n")
        f.write("\n")
        f.write("setup(\n")
        f.write(f'    name="{info.project}",\n')
        f.write("    version=get_version(),\n")
        f.write(f'    author="{info.author}",\n')
        f.write(f'    author_email="{info.email}",\n')
        f.write(f'    description="{info.description}",\n')
        f.write('    license="GPLv3",\n')
        f.write(f'    keywords=("{info.keywords}"),\n')
        f.write(f'    url="{info.repository}",\n')
        f.write("    project_urls={\n")
        f.write(f'        "Source": "{info.repository}",\n')
        f.write(f'        "Tracker": "{info.repository}/issues",\n')
        f.write("    },\n")
        f.write("    packages=find_packages(),\n")
        f.write('    long_description_content_type="text/x-rst; charset=utf-8",\n')
        f.write('    long_description=read("README.rst"),\n')
        f.write("    install_requires=[],\n")
        f.write('    python_requires=">=3.7",\n')
        f.write("    include_package_data=True,\n")
        f.write("    classifiers=[\n")
        f.write('        "Programming Language :: Python :: 3",\n')
        f.write('        "Programming Language :: Python :: 3.7",\n')
        f.write('        "Programming Language :: Python :: 3.8",\n')
        f.write(
            '        "Programming Language :: Python :: Implementation :: CPython",\n'
        )
        f.write("    ],\n")
        f.write('    entry_points={"console_scripts": []},\n')
        f.write(")\n")


def _create_tox(info: Info) -> None:
    # pylint: disable=too-many-statements
    with Path.cwd().joinpath("tox.ini").open("w") as f:
        f.write("[tox]\n")
        f.write("envlist =\n")
        f.write("    flake8, mypy, pylint, black\n")
        f.write("    py{37,38,39},\n")
        f.write("\n")
        f.write("[default]\n")
        f.write("basepython=python3.8\n")
        f.write("\n")
        f.write("[testenv]\n")
        f.write("description = run test\n")
        f.write("basepython =\n")
        f.write("    py37: python3.7\n")
        f.write("    py38: python3.8\n")
        f.write("    py39: python3.9\n")
        f.write("deps =\n")
        f.write(f"    pytest=={info.pytest}\n")
        f.write(f"    pytest-timeout=={info.pytest_timeout}\n")
        f.write("commands = pytest\n")
        f.write("\n")
        f.write("[pytest]\n")
        f.write("addopts = --doctest-modules --doctest-ignore-import-errors\n")
        f.write(f"testpaths = tests {info.project} README.rst\n")
        f.write(
            "markers = slow: marks tests as slow (deselect with '-m \"not slow\"')\n"
        )
        f.write("\n")
        f.write("[testenv:flake8]\n")
        f.write("description = run flake8 (linter)\n")
        f.write("basepython = {[default]basepython}\n")
        f.write("skip_install = True\n")
        f.write("deps =\n")
        f.write(f"    flake8=={info.flake8}\n")
        f.write(f"    flake8-isort=={info.flake8_isort}\n")
        f.write("commands =\n")
        f.write(f"    flake8 --isort-show-traceback {info.project} tests setup.py\n")
        f.write("\n")
        f.write("[testenv:pylint]\n")
        f.write("description = run pylint (static code analysis)\n")
        f.write("basepython = {[default]basepython}\n")
        f.write("deps =\n")
        f.write(f"    pylint=={info.pylint}\n")
        f.write(f"commands = pylint {info.project}\n")
        f.write("\n")
        f.write("[testenv:mypy]\n")
        f.write("description = run mypy (static type checker)\n")
        f.write("description = run mypy (static type checker)\n")
        f.write("basepython = {[default]basepython}\n")
        f.write("deps =\n")
        f.write(f"    mypy=={info.mypy}\n")
        f.write("commands = mypy\n")
        f.write("\n")
        f.write("[testenv:black]\n")
        f.write("description = check that comply with autoformating\n")
        f.write("basepython = {[default]basepython}\n")
        f.write("deps =\n")
        f.write(f"    black=={info.black}\n")
        f.write("commands = black --check --diff\n")
