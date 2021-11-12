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

import re
import sys
import zlib
import base45
import json
import cbor2
import pytz

from datetime import datetime
from cose.headers import KID, Algorithm
from cose.messages import CoseMessage

from greenpass.data import TestType
from greenpass.data import GreenPassKeyManager


class UnrecognizedException(Exception):
    def __init__(self, m):
        """The greenpass was unrecognized."""
        super(UnrecognizedException, self).__init__(m)


class TestResult(object):
    def __init__(self, t):
        """Get the test result parsing the certificate data."""
        self.t = int(t)

    def is_positive(self):
        return self.t == 260373001

    def is_negative(self):
        return self.t == 260415000

    def is_aladeen(self):
        return not self.is_positive() and not self.is_negative()

    def is_unknown(self):
        return self.is_aladeen()

    def __str__(self):
        """Readable format for test result."""
        if self.is_positive():
            return "Positive"
        elif self.is_negative():
            return "Negative"
        return "Unknown"


def _parse_timestamp(d):
    return datetime.fromtimestamp(d, pytz.utc)


def _parse_date_time(d):
    try:
        # strptime on Python < 3.7 does not correctly parse the
        # timezone format with a colon inside, remove the colon
        # in the timezone specification.
        rgx = r"""
        (
            \d{4}-\d{2}-\d{2}T # Date
            \d{2}:\d{2}:\d{2}  # Time
        )
        (
            [+-]
            \d{2}              # Timezone hours
            (?::\d{2})         # Timezone minutes
        )?
        """
        compiled_regex = re.compile(rgx, re.VERBOSE)
        r = compiled_regex.match(d)
        date = r.group(1)
        zone = r.group(2)

        if zone is None:
            date += "+0000"
        else:
            date += r.group(2).replace(":", "")

        testcollectiondate = datetime.strptime(
            date, "%Y-%m-%dT%H:%M:%S%z"
        )
    except Exception as e:
        print(e, file=sys.stderr)
        testcollectiondate = 0
    return testcollectiondate


def _parse_date(d):
    if "T" in d:
        d = _parse_date_time(d)
    else:
        d = datetime.strptime(d, "%Y-%m-%d")
        d = pytz.utc.localize(d, is_dst=None).astimezone(pytz.utc)
    return d


class Certificate(object):
    def __init__(self, k):
        """Certificate class transcription."""
        self.k = k
        self.release_date = None
        self.expiration_date = None
        self.dose_number = None
        self.total_doses = None
        self.validity_from = None
        self.validity_until = None
        self.vaccine_pn = None
        self.vaccine_date = None
        self.test_type = None
        self.target_disease = None
        self.test_collection_date = None
        self.certificate_id = None
        self.expired = False
        self.hours_to_valid = None
        self.remaining_hours = None
        self.blocklisted = False
        self.sign_alg = None
        self.kid = None
        self._type = None
        self.test_result = None
        self.verified = None
        self.manufacturer = None
        self.date_of_collection = None
        self.vaccination_date = None
        self.vaccine_type = None

        self.info = {
            "qr": {},
            "personal": {},
            "cert": {}
        }

        # Filter table to process data
        self.filter_table = {
            self.k.get_target_disease()[1]:     self.set_target_disease,
            self.k.get_dose_number()[1]:        self.set_dose_number,
            self.k.get_total_doses()[1]:        self.set_total_doses,
            self.k.get_certificate_id()[1]:     self.set_certificate_id,
            self.k.get_validity_from()[1]:      self.set_validity_from,
            self.k.get_validity_until()[1]:     self.set_validity_until,
            self.k.get_vaccine_type()[1]:       self.set_vaccine_type,
            self.k.get_test_type()[1]:          self.set_test_type,
            self.k.get_manufacturer()[1]:       self.set_manufacturer,
            self.k.get_vaccine_pn()[1]:         self.set_vaccine_pn,
            self.k.get_release_date()[1]:       self.set_release_date,
            self.k.get_expiration_date()[1]:    self.set_expiration_date,
            self.k.get_date_of_collection()[1]: self.set_date_of_collection,
            self.k.get_vaccination_date()[1]:   self.set_vaccination_date,
            self.k.get_test_result()[1]:        self.set_test_result,
        }

    # Unstructured data (just for print, not used)
    def set_info(self, _type, key, val):
        self.info[_type][key] = val

    def get_info(self):
        return self.info

    def get_target_disease(self):
        return self.target_disease

    def set_target_disease(self, val):
        self.target_disease = val

    def get_release_date(self):
        return self.release_date

    def set_release_date(self, val):
        self.release_date = _parse_timestamp(val)

    def get_expiration_date(self):
        return self.expiration_date

    def set_expiration_date(self, val):
        self.expiration_date = _parse_timestamp(val)

    def get_dose_number(self):
        return self.dose_number

    def set_dose_number(self, val):
        self.dose_number = val

    def get_total_doses(self):
        return self.total_doses

    def set_total_doses(self, val):
        self.total_doses = val

    def get_validity_from(self):
        return self.validity_from

    def set_validity_from(self, val):
        self.validity_from = _parse_date(val)

    def get_validity_until(self):
        return self.validity_until

    def set_validity_until(self, val):
        self.validity_until = _parse_date(val)

    def get_vaccine_pn(self):
        return self.vaccine_pn

    def set_vaccine_pn(self, val):
        self.vaccine_pn = val

    def get_vaccination_date(self):
        return self.vaccination_date

    def set_vaccination_date(self, val):
        self.vaccination_date = _parse_date(val)

    def get_test_type(self):
        return self.test_type

    def set_test_type(self, val):
        self.test_type = val

    def get_manufacturer(self):
        return self.manufacturer

    def set_manufacturer(self, val):
        self.manufacturer = val

    def get_vaccine_type(self):
        return self.vaccine_type

    def set_vaccine_type(self, val):
        self.vaccine_type = val

    def get_test_result(self):
        return self.test_result

    def set_test_result(self, val):
        self.test_result = TestResult(val)

    def get_date_of_collection(self):
        return self.date_of_collection

    def set_date_of_collection(self, val):
        self.date_of_collection = _parse_date(val)

    def get_certificate_id(self):
        return self.certificate_id

    def set_certificate_id(self, val):
        self.certificate_id = val

    def get_expired(self):
        return self.expired

    def set_expired(self, val):
        self.expired = val

    def get_hours_to_valid(self):
        return self.hours_to_valid

    def set_hours_to_valid(self, val):
        self.hours_to_valid = val

    def get_remaining_hours(self):
        return self.remaining_hours

    def set_remaining_hours(self, val):
        self.remaining_hours = val

    def get_blocklisted(self):
        return self.blocklisted

    def set_blocklisted(self, val):
        self.blocklisted = val

    def get_sign_alg(self):
        return self.sign_alg

    def set_sign_alg(self, val):
        self.sign_alg = val

    def get_kid(self):
        return self.kid

    def set_kid(self, val):
        self.kid = val

    def set_parent(self, p):
        self.parent = p

    def set_key(self, k):
        self.parent.set_key(k)

    def verify(self):
        return self.parent.verify()

    def get_type(self):
        # Calculate type if not set
        if self._type is None:
            if self.get_vaccine_type() is not None and \
               self.get_vaccination_date() is not None:
                self._type = "vaccine"
            if self.get_date_of_collection() is not None and \
               self.get_test_type() is not None:
                self._type = "test"
            if self.get_validity_from() is not None and \
               self.get_validity_until() is not None:
                self._type = "recovery"

        return self._type

    def set_verified(self, val):
        self.verified = val

    def get_verified(self):
        return self.verified

    def is_negative(self):
        if self.get_type() != "test":
            return True

        tr = self.get_test_result()
        if tr is None:
            return False
        return tr.is_negative()

    def add_info(self, _type, key, val):
        # Filter none value
        if val is None:
            return
        process_function = self.filter_table.get(key, None)
        # Filter value used to verify the validity of the
        # certificate
        if process_function is not None:
            process_function(val)
        else:
            self.set_info(_type, key, val)


# Parse a green pass file
class GreenPassParser(object):
    def __init__(self, certification, k=GreenPassKeyManager()):
        """Parse the certificate and create a Certificate class."""
        self.k = k
        # Remove the initial HC1: part and decode the certificate
        data = b":".join(certification.strip().split(b":")[1::])
        decoded = base45.b45decode(data)
        uncompressed = zlib.decompress(decoded)

        # Get the COSE message
        self.cose = CoseMessage.decode(uncompressed)

        # Extract kid and payload
        self.kid = self.get_kid_from_cose(self.cose.phdr, self.cose.uhdr)
        self.payload = cbor2.loads(self.cose.payload)

        self.qr_info = {
            k.get_release_country()[1]: self.payload[
                k.get_release_country()[0]
            ],

            k.get_release_date()[1]:    int(self.payload[
                k.get_release_date()[0]
            ]),

            k.get_expiration_date()[1]: int(self.payload[
                k.get_expiration_date()[0]
            ]),
        }

        personal_data = self.payload[k.get_personal_data()[0]][
            k.get_personal_info()[0]
        ]
        self.personal_info = {
            k.get_version()[1]:       personal_data[k.get_version()[0]],
            k.get_date_of_birth()[1]: personal_data[k.get_date_of_birth()[0]],
            k.get_first_name()[1]:    personal_data[k.get_name()[0]][
                k.get_first_name()[0]
            ],
            k.get_last_name()[1]:     personal_data[k.get_name()[0]][
                k.get_last_name()[0]
            ],
        }

        self.certificate_info = []
        if personal_data.get(k.get_vaccine()[0], None) is not None:
            # Vaccine
            self.certificate_type = k.get_vaccine()[0]
        elif personal_data.get(k.get_test()[0], None) is not None:
            # Test
            self.certificate_type = k.get_test()[0]
        elif personal_data.get(k.get_recovery()[0], None) is not None:
            # Recovery
            self.certificate_type = k.get_recovery()[0]
        else:
            raise UnrecognizedException("Unrecognized certificate type")

        for el in personal_data[self.certificate_type]:
            cert = {
                # Common
                k.get_target_disease()[1]:      el[
                    k.get_target_disease()[0]
                ],

                k.get_vaccination_country()[1]: el[
                    k.get_vaccination_country()[0]
                ],

                k.get_certificate_issuer()[1]:  el[
                    k.get_certificate_issuer()[0]
                ],

                k.get_certificate_id()[1]:      el[
                    k.get_certificate_id()[0]
                ],

                # Recovery
                k.get_first_positive_test()[1]: el.get(
                    k.get_first_positive_test()[0], None
                ),

                k.get_validity_from()[1]:       el.get(
                    k.get_validity_from()[0], None
                ),

                k.get_validity_until()[1]:      el.get(
                    k.get_validity_until()[0], None
                ),

                # Common for Test and Vaccine
                k.get_manufacturer()[1]:        el.get(
                    k.get_manufacturer()[0], None
                ),

                # Test
                k.get_test_type()[1]:           el.get(
                    k.get_test_type()[0], None
                ),

                k.get_test_name()[1]:           el.get(
                    k.get_test_name()[0], None
                ),

                k.get_date_of_collection()[1]:  el.get(
                    k.get_date_of_collection()[0], None
                ),

                k.get_test_result()[1]:         el.get(
                    k.get_test_result()[0], None
                ),

                k.get_testing_center()[1]:      el.get(
                    k.get_testing_center()[0], None
                ),

                # Vaccine
                k.get_dose_number()[1]:         int(el.get(
                    k.get_dose_number()[0], 0
                )),

                k.get_total_doses()[1]:         int(el.get(
                    k.get_total_doses()[0], 0
                )),

                k.get_vaccine_pn()[1]:          el.get(
                    k.get_vaccine_pn()[0], None
                ),

                k.get_vaccine_type()[1]:        el.get(
                    k.get_vaccine_type()[0], None
                ),

                k.get_vaccination_date()[1]:    el.get(
                    k.get_vaccination_date()[0], None
                )

            }
            self.certificate_info.append(cert)

    # Return the signature from COSE object
    def get_sign_from_cose(self):
        return self.cose.signature

    # Return the headers from COSE object
    def get_headers_from_cose(self):
        return self.cose.phdr, self.cose.uhdr

    # Isolate KID from COSE object
    @staticmethod
    def get_kid_from_cose(phdr, uhdr):
        for k in phdr.keys():
            if (isinstance(KID(), k)):
                return phdr[k]
        for k in uhdr.keys():
            if (isinstance(KID(), k)):
                return uhdr[k]
        print("Could not find KID", file=sys.stderr)
        return None

    # Get Key ID from the QRCode
    def get_kid(self):
        return self.kid

    def get_sign_alg(self):
        alg = None
        for k in self.cose.phdr.keys():
            if (isinstance(Algorithm(), k)):
                alg = self.cose.phdr[k]
        for k in self.cose.uhdr.keys():
            if (isinstance(Algorithm(), k)):
                alg = self.coseuhdr[k]

        if alg is None:
            print("Could not find Algorithm", file=sys.stderr)
            return None

        return alg.fullname

    # Set the decryption key
    def set_key(self, key):
        self.cose.key = key

    # Verify the code
    def verify(self):
        return self.cose.verify_signature()

    # Dump the content of the payload in JSON format
    def dump(self, om):
        om.rawdump(json.dumps(self.payload))

    def get_certificate(self):
        c = Certificate(self.k)
        # Invalid GP, more than one certificate info
        if len(self.certificate_info) > 1:
            return None

        for qr_info in self.qr_info.items():
            c.add_info("qr", qr_info[0], qr_info[1])
        for personal_info in self.personal_info.items():
            c.add_info("personal", personal_info[0], personal_info[1])
        for cert_info in self.certificate_info[0].items():
            c.add_info("cert", cert_info[0], cert_info[1])

        c.set_sign_alg(self.get_sign_alg())
        c.set_kid(self.get_kid())

        c.set_parent(self)

        return c


# Logic Manager, retrieve information from the certificate and set
#  output.
class LogicManager(object):
    def __init__(self, cachedir):
        """Verification of the certificate."""
        self.cachedir = cachedir

    # Verify certificate
    @staticmethod
    def verify_certificate(cert, sm, cup,
                           enable_blocklist=True,
                           raw=False,
                           k=GreenPassKeyManager(),
                           verificator_key=None):

        expired = False
        blocklisted = False
        hours_to_valid = None
        remaining_hours = None

        dn = cert.get_dose_number()
        sd = cert.get_total_doses()
        positive = not cert.is_negative()
        recovery_from = cert.get_validity_from()
        recovery_until = cert.get_validity_until()
        vaccine = cert.get_vaccine_pn()
        testtype = cert.get_test_type()
        vaccinedate = cert.get_vaccination_date()
        testcollectiondate = cert.get_date_of_collection()
        cert_id = cert.get_certificate_id()

        certificate_type = cert.get_type()

        # Check test validity
        if certificate_type == "test":
            ttype = TestType(testtype)
            hours_to_valid, remaining_hours = sm.get_test_remaining_time(
                testcollectiondate, ttype.get_type()
            )

        # Check vaccine validity
        if certificate_type == "vaccine":
            hours_to_valid, remaining_hours = sm.get_vaccine_remaining_time(
                vaccinedate, vaccine, dn == sd
            )

        # Check recovery validity
        if certificate_type == "recovery":
            hours_to_valid, remaining_hours = sm.get_recovery_remaining_time(
                recovery_from, recovery_until
            )

        if hours_to_valid is not None and remaining_hours is not None:
            if hours_to_valid < 0:
                expired = True
            elif remaining_hours <= 0:
                expired = True
            else:
                expired = False

        blocklisted = enable_blocklist and sm.check_uvci_blocklisted(cert_id)

        cert.set_expired(expired)
        cert.set_hours_to_valid(hours_to_valid)
        cert.set_remaining_hours(remaining_hours)

        # Check blocklist by ID
        cert.set_blocklisted(blocklisted)

        alg = cert.get_sign_alg()
        key = cup.get_key_coseobj(cert.get_kid(), alg=alg)
        cert.set_key(key)
        verified = cert.verify()

        unknown_cert = not cert.get_type() == "vaccine"
        unknown_cert = unknown_cert and not cert.get_type() == "test"
        unknown_cert = unknown_cert and not cert.get_type() == "recovery"

        cert.set_verified(verified)

        valid = verified
        valid = valid and not expired
        valid = valid and not positive
        valid = valid and not unknown_cert
        valid = valid and not blocklisted
        return valid
