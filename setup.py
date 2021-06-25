# -*- coding: utf-8 -*-

# Learn more: https://pyett.readthedocs.io/

from setuptools import setup, find_packages


with open("README.md") as fh:
    readme = fh.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='pyETT',
    version='0.1.5',
    description='Python library for Eleven VR Table Tennis data',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Tharsis T. P. Souza',
    url='https://pyett.readthedocs.io/',
    license=license,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests==2.22.0', 'pandas==1.0.3', 'nbsphinx==0.8.6']
)
