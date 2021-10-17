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
from termcolor import colored

from greenpass.data import *

class NoneOutput(object):
    def __init__(self, colored=colored):
        pass

    def add_general_info(self, infoname, infoval):
        pass

    def add_cert_info(self, infoname, infoval):
        pass

    def add_general_info_ok(self, infoname, infoval):
        pass

    def add_general_info_info(self, infoname, infoval):
        pass

    def add_general_info_warning(self, infoname, infoval):
        pass

    def add_general_info_error(self, infoname, infoval):
        pass

    def add_cert_info_ok(self, infoname, infoval):
        pass

    def add_cert_info_info(self, infoname, infoval):
        pass

    def add_cert_info_warning(self, infoname, infoval):
        pass

    def add_cert_info_error(self, infoname, infoval):
        pass

    def add_remaining_time(self, certtype, certdate, level, remaining_days):
        pass

    def get_not_yet_valid(self, remaining_hours):
        pass

    def get_expired(self, remaining_hours):
        pass

    def get_hours_left(self, remaining_hours):
        pass

    def get_months_left(self, remaining_hours):
        pass

    def dump(self, file=sys.stdout):
        pass

    def dump_settings(self, sm):
        pass

    def rawdump(self, data):
        pass

# Output Manager, manages output and dumps to files and stdout
class OutputManager(NoneOutput):

    def __init__(self, colored=colored):
        self.out = ""
        self.colored = colored

    def add_general_info(self, infoname, infoval):
        self.out += "{:30s} {}\n".format(infoname, infoval)

    def add_cert_info(self, infoname, infoval):
        self.out += "  {:28s} {}\n".format(infoname, infoval)

    def add_general_info_ok(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "green"))

    def add_general_info_info(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "blue"))

    def add_general_info_warning(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "yellow"))

    def add_general_info_error(self, infoname, infoval):
        self.add_general_info(infoname, self.colored(infoval, "red"))

    def add_cert_info_ok(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "green"))

    def add_cert_info_info(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "blue"))

    def add_cert_info_warning(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "yellow"))

    def add_cert_info_error(self, infoname, infoval):
        self.add_cert_info(infoname, self.colored(infoval, "red"))

    def add_remaining_time(self, certtype, certdate, level, remaining_days):
        if level == 0:
            color = "white"
        if level == 1:
            color = "green"
        if level == 2:
            color = "yellow"
        if level == 3:
            color = "red"

        self.out += "  {:28s} {} ({})\n".format(
            "{} Date".format(certtype),
            self.colored(certdate, color),
            self.colored(remaining_days, color)
        )

    def get_not_yet_valid(self, hours_to_valid):
        return "Not yet valid, {:.0f} hours to validity, {} days".format(
                hours_to_valid, int(hours_to_valid / 24)
        )

    def get_expired(self, remaining_hours):
        return "Expired since {:.0f} hours, {} days".format(
                    -remaining_hours,
                    -int(remaining_hours / 24)
                )
    def get_hours_left(self, remaining_hours):
        return "{:.0f} hours left ({} days)".format(
                    remaining_hours,
                    int(remaining_hours / 24)
                )

    def get_months_left(self, remaining_hours):
        return "{:.0f} hours left, {} days, ~ {} months".format(
                remaining_hours,
                int(remaining_hours / 24),
                round(remaining_hours / 24 / 30)
        )

    def dump(self, file=sys.stdout):
        print(self.out, file=file)


    def dump_settings(self, sm):
        print("Tests")
        for el in sm.test.items():
            print("  {} not before: {:4d} hours not after: {:4d} hours".format(
                self.colored("{:25s}".format(el[0]), "blue"),
                el[1]["start_hours"],
                el[1]["end_hours"])
            )

        print("\nCertifications")
        print("  {} not before: {:4d} days  not after: {:4d} days".format(
            self.colored("{:25s}".format("recovery"), "blue"),
            sm.recovery["start_day"],
            sm.recovery["end_day"])
        )

        print("\nVaccines")
        for vac in sm.vaccines.items():
            for el in vac[1].items():
                print("  {} {} not before: {:4d} days  not after: {:4d} days".format(
                    self.colored("{:12s}".format(el[0]), "blue"),
                    self.colored("{:12s}".format(Vaccine(vac[0]).get_pretty_name()), "yellow"),
                    el[1]["start_day"], el[1]["end_day"]
                ))
        print()

    def rawdump(self, data):
        print(data)

