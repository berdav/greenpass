#!/usr/bin/env python3

# Green Pass Parser
# Copyright (C) 2021  Davide Berardi -- <berardi.dav@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import shutil
from distutils.core import setup
import setuptools

maintool = "greenpass"

build_scripts = os.path.join("build", "scripts")

maintool_dst_path = os.path.join(build_scripts, maintool)

os.makedirs(build_scripts, exist_ok=True)
shutil.copyfile(maintool + ".py", maintool_dst_path)

with open("README.md") as f:
    description = f.read()

setup(
    name             = 'greenpass',
    scripts          = [ maintool_dst_path ],
    version          = '3.4',
    license          = 'LGPLv3',
    description      = 'Scriptable green pass verifier',
    long_description = description,
    long_description_content_type='text/markdown',
    packages         = [ "greenpass" ],
    author           = 'Davide Berardi',
    author_email     = 'berardi.dav@gmail.com',
    url              = 'https://github.com/berdav/greenpass',
    download_url     = 'https://github.com/berdav/greenpass/archive/refs/tags/v3.4.zip',
    keywords         = [ 'covid19', 'greenpass', 'certificates', 'authorization' ],
    install_requires = [
        'base45',
        'bs4',
        'PyMuPDF',
        'pytz',
        'cbor2',
        'colorama',
        'Pillow',
        'pyasn1',
        'pyOpenSSL',
        'pyzbar',
        'requests',
        'termcolor',
        'cose'
    ],
    classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)
