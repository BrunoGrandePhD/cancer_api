#! /usr/bin/env python

from setuptools import setup
import oncopy

setup(
    name='oncopy',
    version=oncopy.__version__,
    description='A Python framework and API for handling and storing cancer genomics data and metadata.',
    url='https://github.com/brunogrande/OncoPy',
    author='Bruno Grande',
    author_email='bgrande@sfu.ca',
    license='MIT',
    packages=['oncopy'],
    install_requires=[
        'SQLAlchemy==0.9.8'],
    zip_safe=False
)
