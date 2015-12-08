#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


# should be loaded below
__version__ = None

with open('nbbrowserpdf/_version.py') as version:
    exec(version.read())

setup(
    name="nbbrowserpdf",
    version=__version__,
    description="LaTeX-free PDF generation from Jupyter Notebooks",
    author="Nicholas Bollweg",
    author_email="nbollweg@continuum.io",
    license="BSD-3-Clause",
    url="https://github.com/Anaconda-Server/nbbrowserpdf",
    keywords="ipython jupyter pdf qt webkit",
    classifiers=["Development Status :: 4 - Beta",
                 "Framework :: IPython",
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2",
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: BSD License"],
    packages=["nbbrowserpdf"],
    install_requires=["pypdf2", "ghost.py"],
    include_package_data=True,
    entry_points={
        'console_scripts': ['nbbrowserpdf=nbbrowserpdf.export:main'],
    }
)
