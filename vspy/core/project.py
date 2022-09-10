import itertools
import pathlib
from typing import Dict, Iterable, List, Tuple, Union

from vspy.core.args import Arguments
from vspy.core.clients import fetch_all_requests_data
from vspy.core.file_io import FileWriteJob, path_from_root, process_file_write_jobs


def _static(*args: str) -> pathlib.Path:
    return path_from_root("vspy", "resources", "static", *args)


def _template(*args: str) -> pathlib.Path:
    return path_from_root("vspy", "resources", "templates", *args)


class Project:
    """TODO"""

    _DEV_DEPENDENCIES = [
        "pytest",
        "pytest-timeout",
        "pylint",
        "flake8",
        "flake8-isort",
        "flake8-bugbear",
        "mypy",
        "black",
        "tox",
    ]

    def __init__(self, args: Arguments) -> None:
        self._versions: List[str] = []
        self._dependencies: Dict[str, str] = {}
        self._args: Dict[
            str, Union[str, List[str], Dict[str, str]]
        ] = self._args_from_input(args)
        self._target_root = pathlib.Path(args.target)

    async def create_project(self) -> None:
        """Create template project."""
        await process_file_write_jobs(*self._file_write_jobs())

    async def set_versions(self) -> None:
        """Get versions for dev dependencies and python interpreters."""
        dev_packages, py_versions = await fetch_all_requests_data(
            Project._DEV_DEPENDENCIES
        )
        py_versions.sort(key=Project._version_comparator)
        self._versions.extend(py_versions)
        self._args["py_versions"] = py_versions
        self._dependencies.update(dev_packages)
        self._args["dependencies"] = dev_packages

    def _args_from_input(
        self, args: Arguments
    ) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        return {
            "author": args.author,
            "description": args.description,
            "email": args.email,
            "keywords": " ".join(args.keywords.join(",")),
            "name": args.name,
            "repository": args.repository,
        }

    def _file_write_jobs(self) -> Iterable[FileWriteJob]:
        yield from itertools.chain(
            self._root_files(),
            self._test_files(),
            self._src_files(),
            self._gh_action_files(),
            self._vs_code_files(),
        )

    def _root_files(self) -> Iterable[FileWriteJob]:
        yield FileWriteJob(
            _static("==editor_config=="), self._target_root.joinpath(".editorconfig")
        )
        yield FileWriteJob(
            _template("==isort_cfg=="),
            self._target_root.joinpath(".isort.cfg"),
            self._args,
        )
        yield FileWriteJob(
            _static("==pre_commit=="),
            self._target_root.joinpath(".pre-commit-config.yaml"),
        )
        yield FileWriteJob(
            _static("==empty=="), self._target_root.joinpath("requirements.txt")
        )
        yield FileWriteJob(
            _template("==readme=="),
            self._target_root.joinpath("README.rst"),
            self._args,
        )
        yield FileWriteJob(
            _static("==changelog=="), self._target_root.joinpath("Changelog.md")
        )
        yield FileWriteJob(
            _template("==coveragerc=="),
            self._target_root.joinpath(".coveragerc"),
            self._args,
        )
        yield FileWriteJob(_static("==flake8=="), self._target_root.joinpath(".flake8"))
        yield FileWriteJob(
            _static("==gitignore=="), self._target_root.joinpath(".gitignore")
        )
        yield FileWriteJob(
            _static("==gitattributes=="), self._target_root.joinpath(".gitttribute")
        )
        yield FileWriteJob(
            _template("==isort=="),
            self._target_root.joinpath(".isort.cfg"),
            self._args,
        )
        yield FileWriteJob(
            _template("==pylintrc=="),
            self._target_root.joinpath(".pylintrc"),
            self._args,
        )
        yield FileWriteJob(
            _static("==license=="), self._target_root.joinpath("LICENSE")
        )
        yield FileWriteJob(
            _template("==mypy=="),
            self._target_root.joinpath("mypy.ini"),
            self._args,
        )
        yield FileWriteJob(
            _template("==pyprojecttoml=="),
            self._target_root.joinpath("pyproject.toml"),
            self._args,
        )
        yield FileWriteJob(
            _template("==devdep=="),
            self._target_root.joinpath("requirements-dev.txt"),
            self._args,
        )
        yield FileWriteJob(
            _template("==setuppy=="),
            self._target_root.joinpath("setup.py"),
            self._args,
        )
        yield FileWriteJob(
            _template("==toxini=="),
            self._target_root.joinpath("tox.ini"),
            self._args,
        )
        yield FileWriteJob(
            _template("==manifest=="),
            self._target_root.joinpath("MANIFEST.in"),
            self._args,
        )

    def _test_files(self) -> Iterable[FileWriteJob]:
        group_root = self._target_root.joinpath("tests")
        yield FileWriteJob(_static("==empty=="), group_root.joinpath("__init__.py"))
        yield FileWriteJob(
            _template("==test=="),
            group_root.joinpath("test_placeholder.py"),
            self._args,
        )

    def _src_files(self) -> Iterable[FileWriteJob]:
        name = self._args["name"]
        assert isinstance(name, str)
        group_root = self._target_root.joinpath(name)
        yield FileWriteJob(_static("==init=="), group_root.joinpath("__init__.py"))
        yield FileWriteJob(_static("==main=="), group_root.joinpath("main.py"))

    def _gh_action_files(self) -> Iterable[FileWriteJob]:
        group_root = self._target_root.joinpath(".github")
        yield FileWriteJob(
            _template("==test_and_lint=="),
            group_root.joinpath("test_and_lint.yml"),
            self._args,
        )
        yield FileWriteJob(
            _template("==deploy=="),
            group_root.joinpath("deploy.yml"),
            self._args,
        )

    def _vs_code_files(self) -> Iterable[FileWriteJob]:
        group_root = self._target_root.joinpath(".vscode")
        yield FileWriteJob(
            _static("==vs_config=="), group_root.joinpath("settings.json")
        )

    @staticmethod
    def _version_comparator(version: str) -> Tuple[int, ...]:
        return tuple(map(int, version.split(".")))
