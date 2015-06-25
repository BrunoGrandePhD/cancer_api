#! /usr/bin/env python

from setuptools import setup, find_packages
import cancer_api

setup(
    name="cancer_api",
    version=cancer_api.__version__,
    description="A Python framework and API for handling and "
                "storing cancer genomics data and metadata.",
    url="https://github.com/brunogrande/cancer_api",
    author="Bruno Grande",
    author_email="bgrande@sfu.ca",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 2 :: Only",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License"],
    keywords="bioinformatics cancer genomics framework api",
    packages=find_packages(exclude=["tests"]),
    install_requires=["SQLAlchemy>=0.9.8"]
)
