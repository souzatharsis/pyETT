# -*- coding: utf-8 -*-

# Learn more: https://pyett.readthedocs.io/

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='pyETT',
    version='0.1.0',
    description='Python library for Eleven VR Table Tennis data',
    long_description=readme,
    author='Tharsis T. P. Souza',
    url='https://github.com/souzatharsis/pyETT',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'setup'))
)
