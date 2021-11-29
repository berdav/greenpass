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

import sys

from greenpass.logic import LogicManager, GreenPassParser
from greenpass.settings import SettingsManager
from greenpass.api import CertificateUpdater
from greenpass.output import OutputManager

if __name__ == "__main__":
    out = True
    sm = SettingsManager('')
    om = OutputManager()
    logic = LogicManager('')
    cup = CertificateUpdater()

    data = sys.stdin.read().encode()
    gpp = GreenPassParser(data)
    cert = gpp.get_certificate()
    res = logic.verify_certificate(cert, sm, cup)

    om.print_cert(cert)
    om.dump()

    if res:
        print("[+] Valid")
    else:
        print("[-] Not Valid")

    sys.exit(0)
