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

from greenpass.input import InputTransformer
from greenpass.logic import LogicManager, GreenPassParser
from greenpass.settings import SettingsManager
from greenpass.api import CertificateUpdater
from greenpass.output import NoneOutput

if __name__ == "__main__":
    out = True
    sm = SettingsManager('')
    om = NoneOutput()
    logic = LogicManager('')
    cup = CertificateUpdater()
    for i in sys.argv[1::]:
        try:
            data = InputTransformer(i, 'png').get_data()
            gpp = GreenPassParser(data)
            cert = gpp.get_certificate()
            res = logic.verify_certificate(cert, sm, cup)
        except Exception:
            res = False
        if res:
            print("[+] Valid     {}".format(i))
        else:
            print("[-] Not Valid {}".format(i))

        out = out and res

    sys.exit(out)
