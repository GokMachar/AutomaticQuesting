# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 11:57:31 2022
Setup
@author: Gok
"""
import os
from setuptools import setup, find_packages

__file__ = "A:/Coding/Crypto/dfk/automatic/automatic_questing/setup.py"
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = []  # To populate by reading the requirements file
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(
    name = 'automatic_questing',
    packages = find_packages(),
    description='Python package for DFK automatic questing',
    version='1.0.0',
    url='https://github.com/GokMachar/automatic_questing',
    author='GokMachar',
    author_email='gok.machar.lines@gmail.com',
    keywords= ['DFK', 'questing'],
    install_requires=install_requires,
    )
