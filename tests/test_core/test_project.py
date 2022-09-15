import asyncio
from operator import itemgetter

import pytest
from pytest_httpx import HTTPXMock

from tests.testutils.helpers import TempFile, get_pypi_url_and_res
from tests.testutils.mocks import MockArguments, py_partial_page
from vspy.core.file_io import FileWriteJob, read_file, write_file
from vspy.core.project import Project


async def _setup_and_set_version(
    httpx_mock: HTTPXMock, dir_: str, *packages
) -> Project:
    httpx_mock.add_response(
        url="https://www.python.org/downloads/", content=py_partial_page
    )
    packages = [pck for pck in packages]

    data = [get_pypi_url_and_res(*package) for package in packages]
    for url, res in data:
        httpx_mock.add_response(url=url, json=res)

    args = MockArguments(
        dir_,
        "testproj",
        description="test-des",
        repository="test-repo",
        author="me",
        email="mine",
        keywords="test, example",
    )
    project = Project(args)
    await project.set_versions(list(map(itemgetter(0), packages)))
    return project


@pytest.mark.asyncio
async def test_set_versions(httpx_mock: HTTPXMock):
    with TempFile(0) as (dir_, _):
        project = await _setup_and_set_version(
            httpx_mock, dir_, ("mypck", "0.0.1"), ("mypck2", "19.7.3")
        )
        _args = project._args
        assert len(_args) == 8
        assert tuple(_args["py_versions"]) == ("3.7", "3.8", "3.9", "3.10")
        assert len(_args["dependencies"]) == 2
        assert _args["dependencies"]["mypck"] == "0.0.1"
        assert _args["dependencies"]["mypck2"] == "19.7.3"
        assert _args["author"] == "me"
        assert _args["description"] == "test-des"
        assert _args["email"] == "mine"
        assert _args["keywords"] == "test, example"
        assert _args["name"] == "testproj"
        assert _args["repository"] == "test-repo"


@pytest.mark.asyncio
async def test_create_project(httpx_mock: HTTPXMock):
    with TempFile(4) as (dir_, (src_file1, src_file2, dst_file1, dst_file2)):
        project = await _setup_and_set_version(httpx_mock, dir_, ("tox", "13.22.14"))
        f_content1 = """****
{{name}}
****

subtitle
########

subsubtitle
**********************
"""
        f_content2 = """[tox]
minversion = {{dependencies['tox']}}
envlist =
    flake8, mypy, pylint, black
    py{{'{'}}{{",".join(py_versions).replace(".","")}}{{'}'}},

[default]
basepython=python{{py_versions[-1]}}

[testenv]
description = run test
basepython =
{%- for py_version in py_versions %}
    py{{"".join(py_version.split("."))}}: python{{py_version}}
{%- endfor %}
deps = -rrequirements-dev.txt
commands = pytest
"""
        await asyncio.gather(
            write_file(src_file1, f_content1), write_file(src_file2, f_content2)
        )
        jobs = [
            FileWriteJob(src_file1, dst_file1, True),
            FileWriteJob(src_file2, dst_file2, True),
        ]
        await project.create_project(jobs)
        content1, content2 = await asyncio.gather(
            read_file(dst_file1), read_file(dst_file2)
        )
        assert (
            content1
            == """****
testproj
****

subtitle
########

subsubtitle
**********************
"""
        )
        assert (
            content2
            == """[tox]
minversion = 13.22.14
envlist =
    flake8, mypy, pylint, black
    py{37,38,39,310},

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
"""
        )
