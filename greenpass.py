#!/usr/bin/env python3

# Green Pass Parser
# Copyright (C) 2021  Davide Berardi -- <berardi.dav@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from greenpass.api import *
from greenpass.data import *
from greenpass.input import *
from greenpass.output import *
from greenpass.logic import *
from greenpass.settings import *

import os
import argparse
import colorama
import functools

# Cache Directory
DEFAULT_CACHE_DIR=functools.reduce(
    os.path.join,
    [ os.path.expanduser("~"), ".local", "greenpass" ]
)

if __name__=="__main__":
    parser = argparse.ArgumentParser()

    command = parser.add_mutually_exclusive_group(required=True)

    command.add_argument("--settings",
                         action="store_true",
                         help="Dump VerificaC19 settings")

    command.add_argument("--qr",
                         help="qrcodefile, png format")

    command.add_argument("--pdf",
                         help="qrcodefile, pdf format")

    command.add_argument("--txt",
                         help="read qrcode content from file")

    # Optional Parameters
    parser.add_argument("--cachedir",
                        default=DEFAULT_CACHE_DIR,
                        help="Cache Dir, default:{}".format(DEFAULT_CACHE_DIR))

    parser.add_argument("--raw",
                        action="store_true",
                        help="print raw data of certificate in json format")

    parser.add_argument("--no-color",
                        action="store_true",
                        help="Disable color output")

    parser.add_argument("--no-cache",
                        action="store_true",
                        help="Do not use cache")

    args = parser.parse_args()

    cachedir = args.cachedir
    if args.no_cache:
        cachedir = ''

    res = -1

    if not args.no_color:
        colorama.init()
        from termcolor import colored
    else:
        # Disable colors
        colored=lambda x,y: x

    sm = SettingsManager(cachedir)

    if args.qr != None:
        (path, filetype) = (args.qr, "png")
    if args.pdf != None:
        (path, filetype) = (args.pdf, "pdf")
    if args.txt != None and args.txt != "":
        (path, filetype) = (args.txt, "txt")

    if args.settings != False:
        out = OutputManager(colored)
        out.dump_settings(sm)
        sys.exit(1)

    data = InputTransformer(path, filetype).get_data()
    gpp = GreenPassParser(data)

    out = OutputManager(colored)
    if args.raw:
        gpp.dump(out)
        sys.exit(1)

    logic = LogicManager(cachedir)
    if cachedir != '':
        cup = CachedCertificateUpdater(cachedir)
    else:
        cup = CertificateUpdater()
    res = logic.verify_certificate(out, gpp, sm, cup)

    out.dump()
    sys.exit(res)
