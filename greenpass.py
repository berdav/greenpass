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
from greenpass.output import OutputManager, NoneOutput
from greenpass.logic import GreenPassParser, LogicManager
from greenpass.settings import SettingsManager

import os
import sys
import shutil
import locale
import argparse
import platform
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

    # On windows disable colors by default (CMD currently do not parse)
    parser.add_argument("--no-color",
                        action="store_true",
                        help="Disable color output")

    parser.add_argument("--force-color",
                        action="store_true",
                        help="Force color output")

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

    parser.add_argument("--batch",
                        action="store_true",
                        help="Do not print anything")

    parser.add_argument("--language",
                        help="Select the language, use two letter code")

    return parser.parse_args()


def manage_cache(cachedir, no_cache, clear_cache):
    outcachedir = cachedir
    if no_cache:
        outcachedir = ''
    elif clear_cache:
        shutil.rmtree(outcachedir)

    return outcachedir


def _setup_colors():
    colorama.init()
    from termcolor import colored
    return colored


def _disable_colors():
    def _uncolor(x, y):
        return x
    return _uncolor


def _is_windows():
    return platform.system == "Windows"


def init_colors(no_color, force_color):
    if _is_windows():
        # On windows, CMD do not parse colors, disable them by default
        no_color = True

        # On other systems, terminals usually parse colors, use the
        # passed settings

    if force_color:
        # If Forced, use colored output
        colored = _setup_colors()
    elif no_color:
        # If selected no color do not use colors
        colored = _disable_colors()
    else:
        colored = _setup_colors()

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


def get_language():
    loc = locale.getdefaultlocale()[0]
    if loc is None:
        # Fallback to English
        return "en"
    return loc.split("_")[0]


def main():
    # Get the arguments
    args = setup_argparse()
    # Configure the cache directory
    cachedir = manage_cache(args.cachedir, args.no_cache, args.clear_cache)
    # Configure colored output
    colored = init_colors(args.no_color, args.force_color)

    sm = SettingsManager(cachedir, args.recovery_expiration)

    language = get_language() if args.language is None else args.language

    if args.at_date is not None:
        sm.set_at_date(args.at_date)

    (path, filetype) = get_filetype(args)

    if args.batch:
        om = NoneOutput
    else:
        om = OutputManager

    if args.settings:
        out = om(colored)
        out.dump_settings(sm)
        return 1

    data = InputTransformer(path, filetype).get_data()
    gpp = GreenPassParser(data)

    out = om(colored)
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

    out.print_cert(cert, cachedir=cachedir, language=language)
    out.dump()

    # Unix return code is inverted
    return not res


if __name__ == "__main__":
    sys.exit(main())
