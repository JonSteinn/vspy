#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()


def get_version():
    with open("name/__init__.py", encoding="utf8") as init_file:
        for line in init_file.readlines():
            if line.startswith("__version__"):
                return line.split(" = ")[1].rstrip()[1:-1]
    raise ValueError("Version not found in name/__init__.py")


setup(
    name="name",
    version=get_version(),
    author="Jon Steinn Eliasson",
    author_email="jonsteinn@gmail.com",
    description="DESCRIPTION",
    license="GPLv3",
    keywords=("KEYWORD"),
    url="https://github.com/repo",
    project_urls={
        "Source": "https://github.com/repo",
        "Tracker": "https://github.com/repo/issues",
    },
    packages=find_packages(),
    long_description=read("README.rst"),
    install_requires=[],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
