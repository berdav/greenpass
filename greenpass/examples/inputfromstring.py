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

import sys

from greenpass.input import *
from greenpass.logic import *
from greenpass.settings import *
from greenpass.api import *
from greenpass.output import *

if __name__ == "__main__":
    out = True
    sm = SettingsManager('')
    om = OutputManager()
    logic = LogicManager('')
    cup = CertificateUpdater()

    data = sys.stdin.read().encode()
    gpp = GreenPassParser(data)
    res = logic.verify_certificate(om, gpp, sm, cup)
    om.dump()

    if res:
        print("[+] Valid")
    else:
        print("[-] Not Valid")

    sys.exit(0)
