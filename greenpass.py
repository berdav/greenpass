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

from greenpass.api import CertificateUpdater
from greenpass.api import ForcedCertificateUpdater
from greenpass.api import CachedCertificateUpdater
from greenpass.input import InputTransformer
from greenpass.output import OutputManager
from greenpass.logic import GreenPassParser, LogicManager
from greenpass.settings import SettingsManager

import os
import sys
import shutil
import argparse
import colorama
import functools

# Cache Directory
DEFAULT_CACHE_DIR = functools.reduce(
    os.path.join,
    [os.path.expanduser("~"), ".local", "greenpass"]
)


def setup_argparse():
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

    parser.add_argument("--clear-cache",
                        action="store_true",
                        help="Remove the cache directory")

    parser.add_argument("--key",
                        help="Public certificate to verify the greenpass with")

    parser.add_argument("--verbose",
                        action="store_true",
                        help="Print more information")

    parser.add_argument("--dump-sign",
                        action="store_true",
                        help="Dump the signature included in the certificate")

    parser.add_argument("--no-block-list",
                        action="store_true",
                        help="Do not consider block list")

    parser.add_argument("--at-date",
                        help="Use AT_DATE instead of the current date")

    parser.add_argument("--recovery-expiration",
                        action="store_true",
                        help="Consider the recovery certificate expiration")

    return parser.parse_args()


def manage_cache(cachedir, no_cache, clear_cache):
    outcachedir = cachedir
    if no_cache:
        outcachedir = ''
    elif clear_cache:
        shutil.rmtree(outcachedir)

    return outcachedir


def init_colors(no_color):
    if not no_color:
        colorama.init()
        from termcolor import colored
    else:
        # Disable colors
        def _uncolor(x, y):
            return x
        colored = _uncolor

    return colored


def get_filetype(args):
    (path, filetype) = (None, None)
    if args.qr is not None:
        (path, filetype) = (args.qr, "png")
    if args.pdf is not None:
        (path, filetype) = (args.pdf, "pdf")
    if args.txt is not None and args.txt != "":
        (path, filetype) = (args.txt, "txt")

    return (path, filetype)


def main():
    # Get the arguments
    args = setup_argparse()
    # Configure the cache directory
    cachedir = manage_cache(args.cachedir, args.no_cache, args.clear_cache)
    # Configure colored output
    colored = init_colors(args.no_color)

    sm = SettingsManager(cachedir, args.recovery_expiration)

    if args.at_date is not None:
        sm.set_at_date(args.at_date)

    (path, filetype) = get_filetype(args)

    if args.settings:
        out = OutputManager(colored)
        out.dump_settings(sm)
        return 1

    data = InputTransformer(path, filetype).get_data()
    gpp = GreenPassParser(data)

    out = OutputManager(colored)
    if args.raw:
        gpp.dump(out)
        return 1

    logic = LogicManager(cachedir)

    if args.key is not None:
        cup = ForcedCertificateUpdater(args.key)
    elif cachedir != '':
        cup = CachedCertificateUpdater(cachedir)
    else:
        cup = CertificateUpdater()

    if args.verbose:
        cup.set_verbose()

    if args.dump_sign:
        signature = gpp.get_sign_from_cose()
        phdr, uhdr = gpp.get_headers_from_cose()
        out.dump_cose(phdr, uhdr, signature)
        return 1

    cert = gpp.get_certificate()
    res = logic.verify_certificate(cert, sm, cup,
                                   enable_blocklist=not args.no_block_list)

    out.print_cert(cert, cachedir=cachedir)
    out.dump()

    # Unix return code is inverted
    return not res


if __name__ == "__main__":
    sys.exit(main())
