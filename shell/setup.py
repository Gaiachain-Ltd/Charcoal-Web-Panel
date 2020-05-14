from __future__ import print_function

from setuptools import setup, find_packages

setup(
    name='gaiachain-cli',
    version='0.1',
    description='Gaiachain CLI',
    author='Paweł BB Drozd',
    packages=find_packages(),
    install_requires=[
        'requests', 'click', 'sawtooth_cli'
    ],
    entry_points={
        'console_scripts': [
            'gaiachain = gaiachain_cli.main:main_wrapper'
        ]
    })
