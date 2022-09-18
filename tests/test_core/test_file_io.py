import asyncio
import pathlib

import pytest

from tests.testutils.helpers import TempFile
from vspy.core.file_io import (
    FileWriteJob,
    path_from_root,
    process_file_write_jobs,
    read_file,
    read_json_file,
    template_from_string,
    write_file,
)


@pytest.mark.asyncio
async def test_write_and_read_file():
    with TempFile(1) as (_, (file,)):
        await write_file(file, "abc")
        assert "abc" == await read_file(file)


@pytest.mark.asyncio
async def test_read_json_file():
    with TempFile(1) as (_, (file,)):
        await write_file(file, '{"a": 123, "b": [1,1,2,3,5,8,13]}')
        json = await read_json_file(file)
        assert len(json) == 2
        assert json.get("a", -1) == 123
        assert tuple(json.get("b", [])) == (1, 1, 2, 3, 5, 8, 13)


@pytest.mark.asyncio
async def test_template_from_string():
    tmpl_str = await template_from_string("__{{x}}__", {"x": 3, "y": 5})
    assert tmpl_str == "__3__"


def test_path_from_root():
    assert (
        pathlib.Path(__file__).as_posix()
        == path_from_root("tests", "test_core", "test_file_io.py").as_posix()
    )


@pytest.mark.asyncio
async def test_process_file_write_jobs():
    with TempFile(4) as (_, (src_file1, src_file2, dst_file1, dst_file2)):
        await asyncio.gather(
            write_file(src_file1, "__{{a}}__"), write_file(src_file2, "__X__")
        )
        jobs = [
            FileWriteJob(src_file1, dst_file1, True),
            FileWriteJob(src_file2, dst_file2, False),
        ]
        await process_file_write_jobs(*jobs, args={"a": "some tmpl text"})
        content1, content2 = await asyncio.gather(
            read_file(dst_file1), read_file(dst_file2)
        )
        assert content1 == "__some tmpl text__"
        assert content2 == "__X__"
