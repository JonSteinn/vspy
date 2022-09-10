import asyncio
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import aiofiles
from jinja2 import BaseLoader, Environment

_env = Environment(loader=BaseLoader(), enable_async=True, keep_trailing_newline=True)

_ROOT_DIR = pathlib.Path(__file__).parent.parent.parent


@dataclass
class FileWriteJob:
    """A job unit for processing a template file."""

    source: pathlib.Path
    destination: pathlib.Path
    args: Optional[Dict[str, Union[str, List[str], Dict[str, str]]]] = None


async def write_file(file: pathlib.Path, content: str) -> None:
    """Asynchronous file writing."""
    file.parent.mkdir(exist_ok=True)
    async with aiofiles.open(file.as_posix(), "w", encoding="utf-8") as file_ctx:
        await file_ctx.write(content)


async def read_file(file: pathlib.Path) -> str:
    """Asynchronous file reading."""
    async with aiofiles.open(file.as_posix(), "r", encoding="utf-8") as file_ctx:
        return await file_ctx.read()


async def template_from_string(
    string: str, variables: Dict[str, Union[str, List[str], Dict[str, str]]]
) -> str:
    """Jinja2 wrapper for string templating."""
    return await _env.from_string(string).render_async(**variables)


async def process_file_write_job(job: FileWriteJob) -> None:
    """Process a single file write job."""
    txt = await read_file(job.source)
    if job.args:
        txt = await template_from_string(txt, job.args)
    await write_file(job.destination, txt)


async def process_file_write_jobs(*jobs: FileWriteJob) -> None:
    """Process multiple file write jobs."""
    await asyncio.gather(
        *(asyncio.create_task(process_file_write_job(job)) for job in jobs)
    )


def path_from_root(*args: str) -> pathlib.Path:
    """Get file relative to project root."""
    return _ROOT_DIR.joinpath(*args)
