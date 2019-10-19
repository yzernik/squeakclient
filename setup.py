#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name='squeakclient',
    version='0.1.0',
    license='MIT',
    author='Jonathan Zernik',
    description='Squeak client',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    zip_safe=True,
    keywords=[
        'squeak',
    ],
    install_requires=[
        "squeaklib>=0.1.6",
        "grpcio",
        "grpcio-tools",
    ],
    # other arguments here...
    entry_points={
        'console_scripts': [
            'runsqueak = squeakclient.main:main',
            'runsqueakctl = squeakclient.squeaknode.cli.main:main',
        ],
    },
)
