#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for SaltPyLint
'''
# pylint: disable=file-perms,wrong-import-position
from __future__ import absolute_import, with_statement
import os


BASE_DIR = os.path.dirname(__file__)

INSTALL_REQUIRES = [
    'PyLint>=1.7.1',
    'pycodestyle>=2.3.1',
    'modernize>=0.5'
]

setup_kwargs = {}  # pylint: disable=invalid-name

try:
    from setuptools import setup
    setup_kwargs['install_requires'] = INSTALL_REQUIRES
except ImportError:
    from distutils.core import setup


about = {}  # pylint: disable=invalid-name

with open(os.path.join(BASE_DIR, 'saltpylint', '__about__.py')) as f:
    exec(f.read(), about)  # pylint: disable=exec-used

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author='Pedro Algarvio',
    author_email='pedro@algarvio.me',
    url='https://github.com/saltstack/salt-pylint',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
    ],
    packages=[
        'saltpylint',
        'saltpylint.ext',
        'saltpylint/py3modernize',
        'saltpylint/py3modernize/fixes',
    ],
    **setup_kwargs
)
