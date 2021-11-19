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

from greenpass.data import Disease
from greenpass.data import Manufacturer
from greenpass.data import Vaccine
from greenpass.data import TestType
from greenpass.data import GreenPassKeyManager


class NoneOutput(object):
    def __init__(self, colored=colored):
        """Null output, /dev/null sink."""
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

    def get_not_yet_valid(self, hours_to_valid):
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

    def dump_cose(self, phdr, uhdr, signature):
        pass

    def rawdump(self, data):
        pass

    def print_cert(self, cert, km=GreenPassKeyManager(), cachedir=''):
        pass


# Output Manager, manages output and dumps to files and stdout
class OutputManager(NoneOutput):

    def __init__(self, colored=colored):
        """Default printer manager."""
        self.out = ""
        self.colored = colored

    def add_general_info(self, infoname, infoval):
        if infoval is not None:
            self.out += "{:30s} {}\n".format(infoname, infoval)

    def add_cert_info(self, infoname, infoval):
        if infoval is not None:
            self.out += "  {:28s} {}\n".format(infoname, infoval)

    def add_general_info_ok(self, infoname, infoval):
        if infoval is not None:
            self.add_general_info(infoname, self.colored(infoval, "green"))

    def add_general_info_info(self, infoname, infoval):
        if infoval is not None:
            self.add_general_info(infoname, self.colored(infoval, "blue"))

    def add_general_info_warning(self, infoname, infoval):
        if infoval is not None:
            self.add_general_info(infoname, self.colored(infoval, "yellow"))

    def add_general_info_error(self, infoname, infoval):
        if infoval is not None:
            self.add_general_info(infoname, self.colored(infoval, "red"))

    def add_cert_info_ok(self, infoname, infoval):
        if infoval is not None:
            self.add_cert_info(infoname, self.colored(infoval, "green"))

    def add_cert_info_info(self, infoname, infoval):
        if infoval is not None:
            self.add_cert_info(infoname, self.colored(infoval, "blue"))

    def add_cert_info_warning(self, infoname, infoval):
        if infoval is not None:
            self.add_cert_info(infoname, self.colored(infoval, "yellow"))

    def add_cert_info_error(self, infoname, infoval):
        if infoval is not None:
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
                print((
                    "  {} {} not before: {:4d} days  "
                    "not after: {:4d} days"
                ).format(
                    self.colored("{:12s}".format(el[0]), "blue"),
                    self.colored("{:20s}".format(
                        Vaccine(vac[0]).get_pretty_name()
                    ), "yellow"),
                    el[1]["start_day"], el[1]["end_day"]
                ))

        print("\nBlocked Pass IDs")
        for gp in sm.blocklist:
            print("  {}".format(gp))
        print()

    def dump_cose(self, phdr, uhdr, signature):
        print(self.colored("PHDR:", "green"), phdr)
        print(self.colored("UHDR:", "red"),   uhdr)
        print(self.colored("Sign:", "cyan"),  signature)

    def rawdump(self, data):
        print(data)

    def _print_common_fields(self, cert, km, cachedir):
        self.add_general_info_info(
            "Certificate Type", cert.get_type().capitalize()
        )

        for k, v in cert.get_info()["qr"].items():
            self.add_general_info(k, v)

        self.add_general_info(
            km.get_release_date()[1], cert.get_release_date()
        )

        self.add_general_info(
            km.get_expiration_date()[1], cert.get_expiration_date()
        )

        for k, v in cert.get_info()["personal"].items():
            self.add_general_info(k, v)

        self.add_cert_info_info(
            km.get_target_disease()[1],
            Disease(cert.get_target_disease()).get_pretty_name()
        )
        for k, v in cert.get_info()["cert"].items():
            self.add_cert_info(k, v)

        self.add_cert_info(
            km.get_certificate_id()[1], cert.get_certificate_id()
        )

        if cert.get_blocklisted():
            printfun = self.add_cert_info_error
        else:
            printfun = self.add_cert_info_ok
        printfun(
            km.get_blocklisted()[1], cert.get_blocklisted()
        )

    def _print_vaccine_fields(self, cert, km, cachedir):
        if cert.get_dose_number() == cert.get_total_doses():
            printfun = self.add_cert_info_ok
        else:
            printfun = self.add_cert_info_warning

        if cert.get_total_doses() > 0:
            printfun(
                km.get_doses()[1],
                f"{cert.get_dose_number()}/{cert.get_total_doses()}"
            )

        self.add_cert_info_info(
            km.get_manufacturer()[1],
            Manufacturer(cert.get_manufacturer(), cachedir).get_pretty_name()
        )

        self.add_cert_info_info(
            km.get_vaccine_pn()[1],
            Vaccine(cert.get_vaccine_pn()).get_pretty_name()
        )

        self.add_cert_info(
            km.get_vaccine_type()[1],
            Vaccine(cert.get_vaccine_type()).get_pretty_name()
        )

    def _print_test_fields(self, cert, km, cachedir):
        self.add_cert_info_info(
            km.get_test_type()[1],
            TestType(cert.get_test_type()).get_pretty_name()
        )

        test_result = cert.get_test_result()

        if test_result.is_positive():
            printfun = self.add_cert_info_error
        elif test_result.is_negative():
            printfun = self.add_cert_info_ok
        else:
            printfun = self.add_cert_info_warning
        printfun(
            km.get_test_result()[1],
            test_result
        )

    def _print_recovery_fields(self, cert, km, cachedir):
        self.add_cert_info_info(
            km.get_validity_until()[1],
            cert.get_validity_until()
        )

    def print_cert(self, cert, km=GreenPassKeyManager(), cachedir=''):
        self._print_common_fields(cert, km, cachedir)

        hours_to_valid = cert.get_hours_to_valid()
        remaining_hours = cert.get_remaining_hours()

        if hours_to_valid < 0:
            level = 3
            remaining_days = self.get_not_yet_valid(-hours_to_valid)
        elif remaining_hours <= 0:
            level = 3
            remaining_days = self.get_expired(remaining_hours)
        elif remaining_hours * 24 < 14:
            level = 2
            remaining_hours = self.get_hours_left(remaining_hours)
            remaining_days = remaining_hours
        else:
            level = 1
            remaining_days = self.get_months_left(remaining_hours)

        date = None
        if cert.get_type() == "test":
            self._print_test_fields(cert, km, cachedir)
            date = cert.get_date_of_collection()
        elif cert.get_type() == "vaccine":
            self._print_vaccine_fields(cert, km, cachedir)
            date = cert.get_vaccination_date()
        elif cert.get_type() == "recovery":
            self._print_recovery_fields(cert, km, cachedir)
            date = cert.get_validity_from()

        self.add_remaining_time(
            cert.get_type().capitalize(), date,
            level, remaining_days
        )

        if cert.get_verified():
            printfun = self.add_general_info_ok
        else:
            printfun = self.add_general_info_error
        printfun(
            km.get_verified()[1], cert.get_verified()
        )
