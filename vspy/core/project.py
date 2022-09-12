import pathlib
from typing import Dict, Iterable, List, Tuple, Union

from vspy.core.args import Arguments
from vspy.core.clients import fetch_all_requests_data
from vspy.core.file_io import FileWriteJob, process_file_write_jobs
from vspy.core.type_hints import TemplateArgs


class Project:
    """The project creation class."""

    def __init__(self, args: Arguments) -> None:
        self._versions: List[str] = []
        self._dependencies: Dict[str, str] = {}
        self._args: TemplateArgs = self._args_from_input(args)
        self._target_root = pathlib.Path(args.target)

    async def create_project(self, template_jobs: Iterable[FileWriteJob]) -> None:
        """Create template project."""
        await process_file_write_jobs(*template_jobs, args=self._args)

    async def set_versions(self, dev_dependencies: List[str]) -> None:
        """Get versions for dev dependencies and python interpreters."""
        dev_packages, py_versions = await fetch_all_requests_data(dev_dependencies)
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
            "keywords": args.keywords,
            "name": args.name,
            "repository": args.repository,
        }

    @staticmethod
    def _version_comparator(version: str) -> Tuple[int, ...]:
        return tuple(map(int, version.split(".")))
