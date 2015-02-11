#! /usr/bin/env python

from setuptools import setup
import cancer_api

setup(
    name='cancer_api',
    version=cancer_api.__version__,
    description='A Python framework and API for handling and storing cancer genomics data and metadata.',
    url='https://github.com/brunogrande/cancer_api',
    author='Bruno Grande',
    author_email='bgrande@sfu.ca',
    license='MIT',
    packages=['cancer_api'],
    install_requires=[
        'SQLAlchemy==0.9.8'],
    zip_safe=False
)
