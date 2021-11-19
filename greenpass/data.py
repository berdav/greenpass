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
import sys
import json
import cbor2
import requests

TESTS_URL = (
    "https://covid-19-diagnostics.jrc.ec.europa.eu/devices/export"
)


class GreenPassKeyManager(object):
    def __init__(self):
        """Manage the translation between qrcode keys and readable names."""
        pass

    # The first value of these tuples is the key in the qrcode,
    # the second is the localized info
    @staticmethod
    def get_release_country():
        return (1, "Release Country")

    @staticmethod
    def get_release_date():
        return (6, "Release Date")

    @staticmethod
    def get_expiration_date():
        return (4, "Expiration Date")

    @staticmethod
    def get_version():
        return ("ver", "Version")

    @staticmethod
    def get_date_of_birth():
        return ("dob", "Date of Birth")

    @staticmethod
    def get_name():
        return ("nam", "Name")

    @staticmethod
    def get_personal_data():
        return (-260, "Personal Data")

    @staticmethod
    def get_personal_info():
        return (1, "Personal Info")

    @staticmethod
    def get_first_name():
        return ("gn", "First Name")

    @staticmethod
    def get_last_name():
        return ("fn", "Family Name")

    @staticmethod
    def get_vaccine():
        return ("v", "Vaccine")

    @staticmethod
    def get_test():
        return ("t", "Test")

    @staticmethod
    def get_recovery():
        return ("r", "Recovery")

    @staticmethod
    def get_target_disease():
        return ("tg", "Target Disease")

    @staticmethod
    def get_vaccination_country():
        return ("co", "Vaccination or Test Country")

    @staticmethod
    def get_certificate_issuer():
        return ("is", "Certificate Issuer")

    @staticmethod
    def get_certificate_id():
        return ("ci", "Certificate ID")

    @staticmethod
    def get_first_positive_test():
        return ("fr", "First Positive Test")

    @staticmethod
    def get_validity_from():
        return ("df", "Validity From")

    @staticmethod
    def get_validity_until():
        return ("du", "Validity Until")

    @staticmethod
    def get_manufacturer():
        return ("ma", "Manufacturer and Type")

    @staticmethod
    def get_test_type():
        return ("tt", "Test type")

    @staticmethod
    def get_test_name():
        return ("tn", "Test name")

    @staticmethod
    def get_date_of_collection():
        return ("sc", "Date of collection")

    @staticmethod
    def get_blocklisted():
        return (None, "Blocklisted")

    @staticmethod
    def get_test_result():
        return ("tr", "Test result")

    @staticmethod
    def get_testing_center():
        return ("tc", "Testing center")

    @staticmethod
    def get_dose_number():
        return ("dn", "Dose Number")

    @staticmethod
    def get_total_doses():
        return ("sd", "Total Doses")

    @staticmethod
    def get_vaccine_pn():
        return ("mp", "Vaccine Product Number")

    @staticmethod
    def get_vaccine_type():
        return ("vp", "Vaccine Type")

    @staticmethod
    def get_vaccination_date():
        return ("dt", "Vaccination Date")

    @staticmethod
    def get_certificate_type():
        return ("", "Certificate Type")

    @staticmethod
    def get_verified():
        return ("", "Verified")

    @staticmethod
    def get_doses():
        return ("", "Doses")

    def get_cert_type_long_name(self, t):
        if t == self.get_vaccine()[0]:
            return self.get_vaccine()[1]
        if t == self.get_test()[0]:
            return self.get_test()[1]
        if t == self.get_recovery()[0]:
            return self.get_recovery()[1]


# Vaccine names
class Vaccine(object):
    def __init__(self, t):
        """Translate vaccine code to human-readable name."""
        self.t = t
        self.pretty_name = {
            "EU/1/20/1507": "Moderna",
            "EU/1/20/1525": "Janssen",
            "EU/1/20/1528": "Pfizer",
            "EU/1/21/1529": "AstraZeneca",
            "EU/1/XX/XXX1": "Sputnik-V",
            "EU/1/XX/XXX2": "CVnCoV",
            "EU/1/XX/XXX3": "EpiVacCorona",
            "EU/1/XX/XXX4": "BBIBP-CorV",
            "EU/1/XX/XXX5": "CoronaVac",
        }

    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)


# Manufacturer names
class Manufacturer(object):
    def __init__(self, t, cachedir=''):
        """Translate manufacturer code to human-readable name."""
        self.t = t
        # Vaccines
        self.pretty_name = {
            "ORG-100001699": "AstraZeneca",
            "ORG-100030215": "Biontech",
            "ORG-100001417": "Janssen",
            "ORG-100031184": "Moderna",
            "ORG-100006270": "Curevac",
            "ORG-100013793": "CanSino",
            "ORG-100020693": "Sinopharm",
            "ORG-100010771": "Sinopharm",
            "ORG-100024420": "Sinopharm",
            "ORG-100032020": "Novavax"
        }
        # Testes
        if cachedir == '':
            self.pretty_name.update(self.get_tests_pn())
        else:
            self.pretty_name.update(self.get_cached_tests_pn(cachedir))

    @staticmethod
    def get_tests_pn():
        o = {}
        r = requests.get(TESTS_URL, allow_redirects=True, timeout=10)
        if r.status_code != 200:
            return o
        try:
            tests = json.loads(r.text)
            for el in tests["deviceList"]:
                o[el["id_device"]] = el["commercial_name"]
        # TODO: Be more specific on the exceptions
        except Exception:
            print("Warning: cannot download test data", file=sys.stderr)

        return o

    def get_cached_tests_pn(self, cachedir):
        testcache = os.path.join(cachedir, "tests")

        os.makedirs(cachedir, exist_ok=True)

        if not os.path.exists(testcache):
            with open(testcache, 'wb') as f:
                cbor2.dump(self.get_tests_pn(), f)

        with open(testcache, 'rb') as f:
            try:
                tests = cbor2.load(f)
            except Exception:
                print("Corrupted cache {} removing".format(testcache),
                      file=sys.stderr)
                os.remove(testcache)
                tests = {}

        return tests

    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)


# Disease names
class Disease(object):
    def __init__(self, t):
        """Translate disease code to human-readable name."""
        self.t = t
        self.pretty_name = {
            "840539006": "Covid19"
        }

    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)


class TestType(object):
    def __init__(self, t):
        """Translate test code to human-readable name."""
        self.t = t
        self._type = {
            "LP6464-4":   "molecular",
            "LP217198-3": "rapid"
        }
        self.pretty_name = self._type

    def get_type(self):
        return self._type.get(self.t, self.t)

    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)
