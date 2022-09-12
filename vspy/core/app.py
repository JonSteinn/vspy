import asyncio
import pathlib
from typing import TYPE_CHECKING, List

from vspy.core.args import Arguments
from vspy.core.file_io import (
    FileWriteJob,
    path_from_root,
    read_json_file,
    template_from_string,
)
from vspy.core.project import Project
from vspy.core.utils import clean_dir

if TYPE_CHECKING:
    from vspy.core.type_hints import ConfigData, JobJson


class App:
    """The runnable unit of the package."""

    def __init__(self, args: Arguments) -> None:
        """Initialize the application."""
        self._project = Project(args)
        self._args = args
        self._target = pathlib.Path(args.target)

    async def start(self) -> None:
        """Start the application."""
        dev_dep, jobs = await self._get_config_data()
        await self._project.set_versions(dev_dep)
        await self._project.create_project(jobs)

    async def _get_config_data(self) -> "ConfigData":
        data = await read_json_file(path_from_root("vspy", "resources", "data.json"))
        dev: List[str] = data["dev-dependencies"]
        jobs = await self._proces_file_write_jobs(data["jobs"])
        return dev, jobs

    async def _proces_file_write_jobs(
        self, jobs: List["JobJson"]
    ) -> List[FileWriteJob]:
        return await asyncio.gather(*(self._proces_file_write_job(job) for job in jobs))

    async def _proces_file_write_job(self, job: "JobJson") -> FileWriteJob:
        src = job["src"]
        dst = job["dst"]
        is_template = job["is_template"]
        path_is_template = job["path_is_template"]
        assert (
            isinstance(src, str)
            and isinstance(dst, str)
            and isinstance(is_template, bool)
            and isinstance(path_is_template, bool)
        )
        if path_is_template:
            dst = await template_from_string(dst, {"name": self._args.name})
        return FileWriteJob(
            path_from_root(src), self._target.joinpath(dst), is_template
        )

    def cleanup(self) -> None:
        """Remove any created files."""
        clean_dir(self._target)
