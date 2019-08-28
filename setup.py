#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" setup.py for dataclasses-avroschema."""

from setuptools import setup, find_packages

__version__ = "0.1.0"

with open("README.md") as readme_file:
    long_description = readme_file.read()

requires = ["mypy==0.711"]

setup(
    name="dataclasses-avroschema",
    version=__version__,
    description="Generate Avro Schemas from a Python class",
    long_description=long_description,
    author="Marcos Schroh",
    author_email="schrohm@gmail.com",
    install_requires=requires,
    url="",
    download_url="",
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
    ],
    keywords=(
        """
        Python, Data Classes, Avro Schema, Avro, Apache, Data Streaming
        """
    ),
)