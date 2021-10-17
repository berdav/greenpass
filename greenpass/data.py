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

import json
import requests

TESTS_URL = "https://covid-19-diagnostics.jrc.ec.europa.eu/devices/export?manufacturer=&text_name=&marking=&rapid_diag=&format=&target_type=&field-1=HSC%20common%20list%20%28RAT%29&value-1=1&search_method=AND"

# Static class with common keys for
# printing and addressing in the qrcode
# Can also be localized
class GreenPassKeyManager(object):
    def __init__(self):
        pass

    # The first value of these tuples is the key in the qrcode,
    # the second is the localized info
    def get_release_country(self):
        return ( 1, "Release Country" )

    def get_release_date(self):
        return ( 6, "Release Date" )

    def get_expiration_date(self):
        return ( 4, "Expiration Date" )

    def get_version(self):
        return ( "ver", "Version" )

    def get_date_of_birth(self):
        return ( "dob", "Date of Birth" )

    def get_name(self):
        return ( "nam", "Name" )

    def get_personal_data(self):
        return ( -260, "Personal Data" )

    def get_personal_info(self):
        return ( 1, "Personal Info" )

    def get_first_name(self):
        return ( "gn", "First Name" )

    def get_last_name(self):
        return ( "fn", "Family Name" )

    def get_vaccine(self):
        return ( "v", "Vaccine" )

    def get_test(self):
        return ( "t", "Test" )

    def get_recovery(self):
        return ( "r", "Recovery" )

    def get_target_disease(self):
        return ( "tg", "Target Disease" )

    def get_vaccination_country(self):
        return ( "co", "Vaccination or Test Country" )

    def get_certificate_issuer(self):
        return ( "is", "Certificate Issuer" )

    def get_certificate_id(self):
        return ( "ci", "Certificate ID" )

    def get_first_positive_test(self):
        return ( "fr", "First Positive Test" )

    def get_validity_from(self):
        return ( "df", "Validity From" )

    def get_validity_until(self):
        return ( "du", "Validity Until" )

    def get_manufacturer(self):
        return ( "ma", "Manufacturer and Type" )

    def get_test_type(self):
        return ( "tt", "Test type" )

    def get_test_name(self):
        return ( "tn", "Test name" )

    def get_date_of_collection(self):
        return ( "sc", "Date of collection" )

    def get_test_result(self):
        return ( "tr", "Test result" )

    def get_testing_center(self):
        return ( "tc", "Testing center" )

    def get_dose_number(self):
        return ( "dn", "Dose Number" )

    def get_total_doses(self):
        return ( "sd", "Total Doses" )

    def get_vaccine_pn(self):
        return ( "mp", "Vaccine Product Number" )

    def get_vaccine_type(self):
        return ( "vp", "Vaccine Type" )

    def get_vaccination_date(self):
        return ( "dt", "Vaccination Date" )

    def get_certificate_type(self):
        return ( "", "Certificate Type" )

    def get_verified(self):
        return ( "", "Verified" )

    def get_doses(self):
        return ( "", "Doses" )

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

    def get_tests_pn(self):
        o = {}
        r = requests.get(TESTS_URL, allow_redirects=True, timeout=10)
        if r.status_code != 200:
            return o
        try:
            l = json.loads(r.text)
            for el in l:
                o[el["id_device"]] = el["commercial_name"]
        except:
            pass

        return o

    def get_cached_tests_pn(self, cachedir):
        testcache = os.path.join(cachedir, "tests")

        os.makedirs(cachedir, exist_ok=True)

        if not os.path.exists(testcache):
            with open(testcache, 'wb') as f:
                pickle.dump(self.get_tests_pn(), f)

        with open(testcache, 'rb') as f:
            tests = pickle.load(f)

        return tests

    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)


# Disease names
class Disease(object):
    def __init__(self, t):
        self.t = t
        self.pretty_name = {
            "840539006": "Covid19"
        }
    def get_pretty_name(self):
        return self.pretty_name.get(self.t, self.t)

class TestType(object):
    def __init__(self, t):
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
