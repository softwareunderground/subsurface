# -*- coding: utf 8 -*-
"""
Python installation file.
"""
import sys
from os import path
from setuptools import setup, find_packages

if not sys.version_info[:2] >= (3, 7):
    sys.exit(f"subsurface is only meant for Python 3.7 and up.\n"
             f"Current version: {sys.version_info[0]}.{sys.version_info[1]}.")

this_directory = path.abspath(path.dirname(__file__))

readme = path.join(this_directory, "README.rst")
with open(readme, "r", encoding="utf-8") as f:
    long_description = f.read()
long_description = long_description.split('inclusion-marker')[-1]

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

setup(
    name="subsurface",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    description="Subsurface data types and utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://softwareunderground.github.io/subsurface",
    author="Software Underground",
    author_email="hello@softwareunderground.org",
    license="Apache-2.0",
    install_requires=["xarray", ],
    classifiers=CLASSIFIERS,
    zip_safe=False,
    use_scm_version={
        "root": ".",
        "relative_to": __file__,
        "write_to": path.join("subsurface", "_version.py"),
    },
    setup_requires=["setuptools_scm"],
)
