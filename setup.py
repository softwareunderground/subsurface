# -*- coding: utf 8 -*-
"""
Python installation file.
"""
import os
import sys
from os import path
from setuptools import setup, find_packages

if not sys.version_info[:2] >= (3, 8):
    sys.exit(f"subsurface is only meant for Python 3.8 and up.\n"
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


def read_requirements(file_name, base_path=""):
    # Construct the full path to the requirements file
    full_path = os.path.join(base_path, file_name)
    requirements = []
    with open(full_path, "r", encoding="utf-8") as f:
        for line in f:
            # Strip whitespace and ignore comments
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            # Handle -r directive
            if line.startswith("-r "):
                referenced_file = line.split()[1]  # Extract the file name
                # Recursively read the referenced file, making sure to include the base path
                requirements.extend(read_requirements(referenced_file, base_path=base_path))
            else:
                requirements.append(line)

    print(requirements)
    return requirements


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
    install_requires=read_requirements("requirements.txt", "requirements"),
    extras_require={
            "plog": read_requirements("requirements_plot.txt", "requirements"),
            "opt": read_requirements("requirements_opt.txt", "requirements"),
            "dev": read_requirements("requirements_dev.txt", "requirements"),
            "all": read_requirements("requirements_all.txt", "requirements")
    },
    classifiers=CLASSIFIERS,
    zip_safe=False,
    use_scm_version={
            "root"       : ".",
            "relative_to": __file__,
            "write_to"   : path.join("subsurface", "_version.py"),
    },
    setup_requires=["setuptools_scm"],
)
