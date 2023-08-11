# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 12:18:08 2023

@author: jkris

"""
# SETUP PROCESS BELOW
# cleandoc -d ./../src/{NAME} -w
# python setup.py bdist_wheel sdist
# twine check dist/*
# twine upload dist/*

from os import path
from setuptools import find_packages, setup
from pipreqs.pipreqs import get_all_imports, get_pkg_names, get_import_local

# PARAMETERS
setupdir = path.realpath(__file__)[0]
NAME = path.split(setupdir)[1]
# add code to grab last version pushed to Pypi
VERSION = "0.0.1"
DESC = "Web App for cleaning, searching, editing, and navigating Python code."


with open("README.md", "r", encoding="utf-8") as readme:
    readme_text = readme.read()

imports = get_all_imports(f"./src/{NAME}")
pkgnames = get_pkg_names(imports)
pkgdicts = get_import_local(pkgnames)
pkglist = [pkgdict["name"] + "==" + pkgdict["version"] for pkgdict in pkgdicts]

setup(
    name=NAME,
    version=VERSION,
    description=DESC,
    long_description=readme_text,
    long_description_content_type="text/markdown",
    author="Jason Krist",
    author_email="jkrist2696@gmail.com",
    url=f"https://github.com/jkrist2696/{NAME}",
    license="GNU GPLv3",
    packages=find_packages(where="src"),
    install_requires=pkglist,
    package_dir={f"{NAME}": f"src/{NAME}"},
    entry_points={"console_scripts": [f"{NAME}={NAME}.cli:main"]},
    python_requires=">=3.9",
)
