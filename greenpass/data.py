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


class Localized_GreenPassKeyManager(object):
    def __init__(self):
        """Manage the translation between qrcode keys and readable names."""
        pass

    def get_cert_type_long_name(self, t):
        if t == self.get_vaccine()[0]:
            return self.get_vaccine()[1]
        if t == self.get_test()[0]:
            return self.get_test()[1]
        if t == self.get_recovery()[0]:
            return self.get_recovery()[1]

    def translate_type(self, t):
        if t == "vaccine":
            return self.get_vaccine()[1]
        elif t == "test":
            return self.get_test()[1]
        elif t == "recovery":
            return self.get_recovery()[1]

        return t

    # The first value of these tuples is the key in the qrcode,
    # the second is the localized info
    def get_key(self, k):
        return k, self._data.get(k, k)

    def get_release_country(self):
        return self.get_key(1)

    def get_release_date(self):
        return self.get_key(6)

    def get_expiration_date(self):
        return self.get_key(4)

    def get_version(self):
        return self.get_key("ver")

    def get_date_of_birth(self):
        return self.get_key("dob")

    def get_name(self):
        return self.get_key("nam")

    def get_personal_data(self):
        return self.get_key(-260)

    def get_personal_info(self):
        # Personal info has a special key which clashes with the
        # release country one.
        return 1, self.get_key("_per")[1]

    def get_first_name(self):
        return self.get_key("gn")

    def get_last_name(self):
        return self.get_key("fn")

    def get_vaccine(self):
        return self.get_key("v")

    def get_test(self):
        return self.get_key("t")

    def get_recovery(self):
        return self.get_key("r")

    def get_target_disease(self):
        return self.get_key("tg")

    def get_vaccination_country(self):
        return self.get_key("co")

    def get_certificate_issuer(self):
        return self.get_key("is")

    def get_certificate_id(self):
        return self.get_key("ci")

    def get_first_positive_test(self):
        return self.get_key("fr")

    def get_validity_from(self):
        return self.get_key("df")

    def get_validity_until(self):
        return self.get_key("du")

    def get_manufacturer(self):
        return self.get_key("ma")

    def get_test_type(self):
        return self.get_key("tt")

    def get_test_name(self):
        return self.get_key("tn")

    def get_date_of_collection(self):
        return self.get_key("sc")

    def get_blocklisted(self):
        return self.get_key("_block")

    def get_test_result(self):
        return self.get_key("tr")

    def get_testing_center(self):
        return self.get_key("tc")

    def get_dose_number(self):
        return self.get_key("dn")

    def get_total_doses(self):
        return self.get_key("sd")

    def get_vaccine_pn(self):
        return self.get_key("mp")

    def get_vaccine_type(self):
        return self.get_key("vp")

    def get_vaccination_date(self):
        return self.get_key("dt")

    def get_certificate_type(self):
        return self.get_key("_typ")

    def get_verified(self):
        return self.get_key("_ver")

    def get_doses(self):
        return self.get_key("_dos")

    def get_expired_since(self):
        return self.get_key("_expired_since")

    def get_hours(self):
        return self.get_key("_hours")

    def get_hours_left(self):
        return self.get_key("_hours_left")

    def get_not_yet_valid(self):
        return self.get_key("_not_yet_valid")

    def get_hours_to_validity(self):
        return self.get_key("_hours_to_validity")

    def get_months(self):
        return self.get_key("_months")

    def get_days(self):
        return self.get_key("_days")


class IT_GreenPassKeyManager(Localized_GreenPassKeyManager):
    def __init__(self):
        """Italian localized greenpass strings."""
        self._data = {
            1: "Paese di rilascio",
            6: "Data di rilascio",
            4: "Data di scadenza",
            "ver": "Versione",
            "dob": "Data di Nascita",
            "nam": "Nome",
            -260: "Dati personali",
            "_per": "Informazioni personali",
            "gn": "Nome",
            "fn": "Cognome",
            "v": "Vaccino",
            "t": "Test",
            "r": "Recupero",
            "tg": "Malattia",
            "co": "Paese di vaccinazione o test",
            "is": "Ente di rilascio",
            "ci": "ID Certificato",
            "fr": "Data primo test positivo",
            "df": "Valido da",
            "du": "Valido fino a",
            "ma": "Produttore e tipo",
            "tt": "Tipo di test",
            "tn": "Nome del test",
            "sc": "Data di analisi",
            "dt": "Data di vaccinazione",
            "tr": "Risultato del test",
            "tc": "Centro di test",
            "dn": "Dose numero",
            "sd": "Dosi totali",
            "mp": "Codice del vaccino",
            "vp": "Tipo di vaccino",
            "_typ": "Tipo di certificato",
            "_ver": "Verificato",
            "_dos": "Dosi",
            "_block": "Bloccato",
            "_False": "No",
            "_True": "Sì",
            "_expired_since": "Scaduto da",
            "_hours": "Ore",
            "_hours_left": "Ore rimanenti",
            "_not_yet_valid": "Non ancora valido",
            "_hours_to_validity": "Ore rimanenti per risultare valido",
            "_days": "Giorni",
            "_months": "Mesi"
        }

    @staticmethod
    def get_date_format():
        return "Data {}"


class DE_GreenPassKeyManager(Localized_GreenPassKeyManager):
    def __init__(self):
        """German localized greenpass strings."""
        self._data = {
            1: "Freigabeland",
            6: "Veröffentlichungsdatum",
            4: "Verfallsdatum",
            "ver": "Version",
            "dob": "Geburtsdatum",
            "nam": "Name",
            -260: "Persönliche Daten",
            "_per": "Persönliche Informationen",
            "gn": "Vorname",
            "fn": "Name",
            "v": "Impfung",
            "t": "Prüfung",
            "r": "Erholung",
            "tg": "Zielkrankheit",
            "co": "Impfland",
            "is": "Zertifikataussteller",
            "ci": "Zertifikats-ID",
            "fr": "Erster Positiver Test",
            "df": "Gültigkeit ab",
            "du": "Gültigkeit bis",
            "ma": "Hersteller und Typ",
            "tt": "Testtyp",
            "tn": "Testname",
            "sc": "Datum der Abholung",
            "tr": "Testergebnis",
            "tc": "Testzentrum",
            "dn": "Dosisnummer",
            "sd": "Gesamtdosen",
            "mp": "Impfcode",
            "vp": "Impftyp",
            "dt": "Impfdatum",
            "_typ": "Art des Zertifikats",
            "_ver": "Verifiziert",
            "_dos": "Dosen",
            "_block": "Verstopft",
            "_False": "Nein",
            "_True": "Ja",
            "_expired_since": "Expired Since",
            "_hours": "Stunden",
            "_hours_left": "Stunden übrig",
            "_not_yet_valid": "noch nicht gültig",
            "_hours_to_validity": "Stunden bis Gültigkeit",
            "_days": "Tage",
            "_months": "Monate"
        }

    @staticmethod
    def get_date_format():
        return "{}datum"


class EN_GreenPassKeyManager(Localized_GreenPassKeyManager):
    def __init__(self):
        """English localized greenpass strings."""
        self._data = {
            1: "Release Country",
            6: "Release Date",
            4: "Expiration Date",
            "ver": "Version",
            "dob": "Date of Birth",
            "nam": "Name",
            -260: "Personal Data",
            "_per": "Personal Info",
            "gn": "First Name",
            "fn": "Family Name",
            "v": "Vaccine",
            "t": "Test",
            "r": "Recovery",
            "tg": "Target Disease",
            "co": "Vaccination or Test Country",
            "is": "Certificate Issuer",
            "ci": "Certificate ID",
            "fr": "First Positive Test",
            "df": "Validity From",
            "du": "Validity Until",
            "ma": "Manufacturer and Type",
            "tt": "Test type",
            "tn": "Test name",
            "sc": "Date of collection",
            "tr": "Test result",
            "tc": "Testing center",
            "dn": "Dose Number",
            "sd": "Total Doses",
            "mp": "Vaccine Product Number",
            "vp": "Vaccine Type",
            "dt": "Vaccination Date",
            "_typ": "Certificate Type",
            "_ver": "Verified",
            "_dos": "Doses",
            "_block": "Blocklisted",
            "_False": "False",
            "_True": "True",
            "_expired_since": "Expired Since",
            "_hours": "Hours",
            "_hours_left": "Hours left",
            "_not_yet_valid": "Not yet valid",
            "_hours_to_validity": "Hours to validity",
            "_days": "Days",
            "_months": "Months"
        }

    @staticmethod
    def get_date_format():
        return "{} Date"


class GreenPassKeyManager(object):
    def __init__(self):
        """Dispatch the localized key values."""

    def get_localization(self, language="en"):
        if language == "it":
            return IT_GreenPassKeyManager()
        elif language == "de":
            return DE_GreenPassKeyManager()
        else:
            return EN_GreenPassKeyManager()
        return self.get_default()

    def get_default(self):
        return self.get_localization(language="en")


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
        try:
            r = requests.get(TESTS_URL, allow_redirects=True, timeout=10)
        except requests.exceptions.ReadTimeout:
            # The operation timed out, return empty value
            return o

        if r.status_code != 200:
            # The operation did not succeded, return empty value
            return o

        try:
            tests = json.loads(r.text)
            for el in tests["deviceList"]:
                o[el["id_device"]] = el["commercial_name"]
        # TODO: Be more specific on the exceptions
        except Exception:
            # The data cannot be downloaded, return value correctly parsed
            print("Warning: cannot download test data", file=sys.stderr)
            return o

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
