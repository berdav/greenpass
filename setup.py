#!/usr/bin/env python3
from distutils.core import setup
import setuptools

with open("README.md") as f:
    description = f.read()

setup(
    name             = 'greenpass',
    scripts          = [ "greenpass" ],
    version          = '2.1',
    license          = 'GPLv3',
    description      = 'Scriptable green pass verifier',
    long_description = description,
    long_description_content_type='text/markdown',
    author           = 'Davide Berardi',
    author_email     = 'berardi.dav@gmail.com',
    url              = 'https://github.com/berdav/greenpass',
    download_url     = 'https://github.com/berdav/greenpass/archive/refs/tags/v2.1.zip',
    keywords         = [ 'covid19', 'greenpass', 'certificates', 'authorization' ],
    install_requires = [
        'base45',
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
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Healthcare Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
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
