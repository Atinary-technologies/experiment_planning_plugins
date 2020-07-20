#!/usr/bin/env python

from setuptools import setup, find_packages

# ==============================================================================


def readme():
    with open("README.md", encoding="utf-8") as content:
        return content.read()


# ==============================================================================

setup(
    name="chimera",
    version="0.1.0",
    description="Chimera: enabling hierarchy based multi objective optimization for autonomous experimentation platforms",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Operating System :: Windows/Unix",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
    ],
    author="ChemOS Inc.",
    author_email="florian@chemos.io",
    package_dir={"chimera": "src/chimera"},
    packages=find_packages("src"),
    zip_safe=False,
    python_requires=">=3.6",
)
