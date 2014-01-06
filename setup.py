# pylint: disable=all

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from version import get_git_version
from subprocess import check_output


setup(
    name="nist_lookup",
    version=get_git_version(),
    packages=find_packages(exclude='test'),
    scripts=[
        "bin/nist_lookup.py",
    ],

    install_requires=[
        'numpy==1.7.1',
        'h5py==2.2.0',
        'matplotlib==1.3.1',
        'pypes==1.2',
        'pypesvds==1.1.0',
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },

    # metadata for upload to PyPI
    author="TOMCAT DPC group",
    author_email="",
    description="Download table from the NIST database",
    license="GNU GPL 3",
    keywords="",
    # project home page, if any
    url="https://bitbucket.org/psitomcat/nist_lookup",
    # could also include long_description, download_url, classifiers, etc.
)
