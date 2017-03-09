#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The setup script for SaltPyLint
'''
# pylint: disable=file-perms,wrong-import-position
from __future__ import absolute_import, with_statement
import io
import os
import sys

SETUP_KWARGS = {}
USE_SETUPTOOLS = False

# Change to salt source's directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're most likely being frozen and __file__ triggered this NameError
    # Let's work around that
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])


if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SALT_PYLINT_REQS = os.path.join(os.path.abspath(SETUP_DIRNAME), 'requirements.txt')


def _parse_requirements_file(requirements_file):
    parsed_requirements = []
    with open(requirements_file) as rfh:
        for line in rfh.readlines():
            line = line.strip()
            if not line or line.startswith(('#', '-r')):
                continue
            parsed_requirements.append(line)
    return parsed_requirements

if 'USE_SETUPTOOLS' in os.environ:
    try:
        from setuptools import setup
        USE_SETUPTOOLS = True
        SETUP_KWARGS['install_requires'] = _parse_requirements_file(SALT_PYLINT_REQS)
    except ImportError:
        USE_SETUPTOOLS = False


if USE_SETUPTOOLS is False:
    from distutils.core import setup  # pylint: disable=import-error,no-name-in-module

with io.open(os.path.join(SETUP_DIRNAME, 'saltpylint', 'version.py'), encoding='utf-8') as fh_:
    contents = fh_.read()
    if not isinstance(contents, str):
        contents = contents.encode('utf-8')
    exec(  # pylint: disable=exec-used
        compile(
            contents,
            os.path.join(SETUP_DIRNAME, 'saltpylint', 'version.py'),
            'exec'
        )
    )


NAME = 'SaltPyLint'
VERSION = __version__  # pylint: disable=undefined-variable
DESCRIPTION = (
    'Required PyLint plugins needed in the several SaltStack projects.'
)

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
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
    **SETUP_KWARGS
)
