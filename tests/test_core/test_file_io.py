import pytest

from tests.testutils.helpers import TempFile
from vspy.core.file_io import (
    read_file,
    read_json_file,
    template_from_string,
    write_file,
)


@pytest.mark.asyncio
async def test_write_and_read_file():
    with TempFile(1) as (directory, files):
        file = files.pop()
        await write_file(file, "abc")
        assert "abc" == await read_file(file)


@pytest.mark.asyncio
async def test_read_json_file():
    with TempFile(1) as (directory, files):
        file = files.pop()
        await write_file(file, '{"a": 123, "b": [1,1,2,3,5,8,13]}')
        json = await read_json_file(file)
        assert len(json) == 2
        assert json.get("a", -1) == 123
        assert tuple(json.get("b", [])) == (1, 1, 2, 3, 5, 8, 13)


@pytest.mark.asyncio
async def test_template_from_string():
    tmpl_str = await template_from_string("__{{x}}__", {"x": 3, "y": 5})
    assert tmpl_str == "__3__"
