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
from cose.headers import KID
from cose.messages import CoseMessage

from greenpass.data import *

class UnrecognizedException(Exception):
    def __init__(self, m):
        return super(UnrecognizedException, self).__init__(m)

class TestResult(object):
    def __init__(self, t):
        self.t = t

    def is_positive(self):
        return self.t == 260373001

    def is_negative(self):
        return self.t == 260415000

    def is_aladeen(self):
        return not self.is_positive() and not self.is_negative()

    def is_unknown(self):
        return self.is_aladeen()

    def __str__(self):
        if self.is_positive():
            return "Positive"
        elif self.is_negative():
            return "Negative"
        return "Unknown"

# Parse a green pass file
class GreenPassParser(object):
    def __init__(self, certification, k=GreenPassKeyManager()):
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
            k.get_release_country()[1]: self.payload[k.get_release_country()[0]],
            k.get_release_date()[1]:    int(self.payload[k.get_release_date()[0]]),
            k.get_expiration_date()[1]: int(self.payload[k.get_expiration_date()[0]]),
        }

        personal_data = self.payload[k.get_personal_data()[0]][k.get_personal_info()[0]]
        self.personal_info = {
            k.get_version()[1]:       personal_data[k.get_version()[0]],
            k.get_date_of_birth()[1]: personal_data[k.get_date_of_birth()[0]],
            k.get_first_name()[1]:    personal_data[k.get_name()[0]][k.get_first_name()[0]],
            k.get_last_name()[1]:     personal_data[k.get_name()[0]][k.get_last_name()[0]],
        }

        self.certificate_info = []
        if personal_data.get(k.get_vaccine()[0], None) != None:
            # Vaccine
            self.certificate_type = k.get_vaccine()[0]
        elif personal_data.get(k.get_test()[0], None) != None:
            # Test
            self.certificate_type = k.get_test()[0]
        elif personal_data.get(k.get_recovery()[0], None) != None:
            # Recovery
            self.certificate_type = k.get_recovery()[0]
        else:
            raise UnrecognizedException("Unrecognized certificate type")

        for el in personal_data[self.certificate_type]:
            cert = {
                # Common
                k.get_target_disease()[1]:      el[k.get_target_disease()[0]],
                k.get_vaccination_country()[1]: el[k.get_vaccination_country()[0]],
                k.get_certificate_issuer()[1]:  el[k.get_certificate_issuer()[0]],
                k.get_certificate_id()[1]:      el[k.get_certificate_id()[0]],
                # Recovery
                k.get_first_positive_test()[1]: el.get(k.get_first_positive_test()[0], None),
                k.get_validity_from()[1]:       el.get(k.get_validity_from()[0], None),
                k.get_validity_until()[1]:      el.get(k.get_validity_until()[0], None),
                # Common for Test and Vaccine
                k.get_manufacturer()[1]:        el.get(k.get_manufacturer()[0], None),
                # Test
                k.get_test_type()[1]:           el.get(k.get_test_type()[0], None),
                k.get_test_name()[1]:           el.get(k.get_test_name()[0], None),
                k.get_date_of_collection()[1]:  el.get(k.get_date_of_collection()[0], None),
                k.get_test_result()[1]:         el.get(k.get_test_result()[0], None),
                k.get_testing_center()[1]:      el.get(k.get_testing_center()[0], None),
                # Vaccine
                k.get_dose_number()[1]:         int(el.get(k.get_dose_number()[0], 0)),
                k.get_total_doses()[1]:         int(el.get(k.get_total_doses()[0], 0)),
                k.get_vaccine_pn()[1]:          el.get(k.get_vaccine_pn()[0], None),
                k.get_vaccine_type()[1]:        el.get(k.get_vaccine_type()[0], None),
                k.get_vaccination_date()[1]:    el.get(k.get_vaccination_date()[0], None)
            }
            self.certificate_info.append(cert)

    # Isolate KID from COSE object
    def get_kid_from_cose(self, phdr, uhdr):
        for k in phdr.keys():
            if (k == type(KID())):
                return phdr[k]
        for k in uhdr.keys():
            if (k == type(KID())):
                return uhdr[k]
        print("Could not find KID", file=sys.stderr)
        return None

    # Get Key ID from the QRCode
    def get_kid(self):
        return self.kid

    # Set the decryption key
    def set_key(self, key):
        self.cose.key = key

    # Verify the code
    def verify(self):
        return self.cose.verify_signature()

    # Dump the content of the payload in JSON format
    def dump(self, om):
        om.rawdump(json.dumps(self.payload))

# Logic Manager, retrieve information from the certificate and set
#  output.
class LogicManager(object):

    def __init__(self, cachedir):
        self.cachedir = cachedir
        pass

    # Verify certificate
    def verify_certificate(self,
                           output,
                           gpp,
                           sm,
                           cup,
                           raw=False,
                           k=GreenPassKeyManager(),
                           verificator_key=None):
        dn = -1
        sd = -1

        vaccinedate = None
        recovery_from  = None
        recovery_until = None
        testcollectiondate = None

        expired = True
        vaccine = None
        positive = False
        hours_to_valid = None
        testtype = None
        remaining_hours = None

        certificate_type = k.get_cert_type_long_name(gpp.certificate_type)
        output.add_general_info_info(k.get_certificate_type()[1], certificate_type)

        for qr_info in gpp.qr_info.items():
            if qr_info[0] == k.get_release_date()[1] or qr_info[0] == k.get_expiration_date()[1]:
                output.add_general_info(qr_info[0], datetime.fromtimestamp(qr_info[1], pytz.utc))
            else:
                output.add_general_info(qr_info[0], qr_info[1])

        for personal_info in gpp.personal_info.items():
            output.add_general_info(personal_info[0], personal_info[1])

        # Invalid GP, more than one certificate info
        if len(gpp.certificate_info) > 1:
            return False

        el = gpp.certificate_info[0]

        for cert_info in tuple(filter(lambda x: x[1] != None, el.items())):
            if cert_info[0] == k.get_dose_number()[1]:
                dn = cert_info[1]
            elif cert_info[0] == k.get_test_result()[1]:
                t = TestResult(int(cert_info[1]))
                # Strict check, also unknown do not get validated
                positive = not t.is_negative()
                if positive:
                    output.add_cert_info_error(cert_info[0], t)
                else:
                    output.add_cert_info_ok(cert_info[0], t)
            elif cert_info[0] == k.get_validity_from()[1]:
                try:
                    recovery_from = datetime.strptime(cert_info[1], "%Y-%m-%d")
                    recovery_from = pytz.utc.localize(recovery_from, is_dst=None).astimezone(pytz.utc)
                except Exception as e:
                    print(e, file=sys.stderr)
                    recovery_from = 0
            elif cert_info[0] == k.get_validity_until()[1]:
                try:
                    recovery_until = datetime.strptime(cert_info[1], "%Y-%m-%d")
                    recovery_until = pytz.utc.localize(recovery_until, is_dst=None).astimezone(pytz.utc)
                except Exception as e:
                    print(e, file=sys.stderr)
                    recovery_until = 0
                certdate = recovery_from
            elif cert_info[0] == k.get_total_doses()[1]:
                sd = int(cert_info[1])
            elif cert_info[0] == k.get_vaccine_pn()[1]:
                vaccine = cert_info[1]
                output.add_cert_info_info(cert_info[0], Vaccine(cert_info[1]).get_pretty_name())
            elif cert_info[0] == k.get_test_type()[1]:
                testtype = cert_info[1]
                output.add_cert_info_info(cert_info[0], TestType(cert_info[1]).get_pretty_name())
            elif cert_info[0] == k.get_vaccination_date()[1]:
                try:
                    vaccinedate = datetime.strptime(cert_info[1], "%Y-%m-%d")
                    vaccinedate = pytz.utc.localize(vaccinedate, is_dst=None).astimezone(pytz.utc)
                except Exception as e:
                    print(e, file=sys.stderr)
                    vaccinedate = 0
                certdate  = vaccinedate
            elif cert_info[0] == k.get_date_of_collection()[1]:
                try:
                    # strptime on Python < 3.7 does not correctly parse the timezone
                    # format with a colon inside, remove the colon in the timezone
                    # specification.
                    rgx = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})([+-]\d{2}(?::\d{2}))?"
                    r = re.match(rgx, cert_info[1])
                    date = r.group(1)
                    zone = r.group(2)

                    if zone == None:
                        date += "+0000"
                    else:
                        date += r.group(2).replace(":", "")

                    testcollectiondate = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
                except Exception as e:
                    print(e, file=sys.stderr)
                    testcollectiondate = 0
                certdate = testcollectiondate
            elif cert_info[0] == k.get_manufacturer()[1]:
                output.add_cert_info_info(cert_info[0], Manufacturer(cert_info[1]).get_pretty_name())
            elif cert_info[0] == k.get_target_disease()[1]:
                output.add_cert_info_info(cert_info[0], Disease(cert_info[1]).get_pretty_name())
            else:
                output.add_cert_info(cert_info[0], cert_info[1])

        # Complex fields parse
        if dn > 0 and sd > 0:
            if dn == sd:
                output.add_cert_info_ok(k.get_doses()[1], "{}/{}".format(dn, sd))
            elif dn < sd and dn != 0:
                output.add_cert_info_warning(k.get_doses()[1], "{}/{}".format(dn, sd))

        # Check test validity
        if testcollectiondate != None and testtype != None:
            level = 0
            ttype = TestType(testtype)
            hours_to_valid, remaining_hours = sm.get_test_remaining_time(testcollectiondate, ttype.get_type())

        # Check vaccine validity
        if vaccinedate != None and vaccine != None:
            level = 0
            hours_to_valid, remaining_hours = sm.get_vaccine_remaining_time(vaccinedate, vaccine, dn == sd)

        # Check recovery validity
        if recovery_from != None and recovery_until != None:
            level = 0
            hours_to_valid, remaining_hours = sm.get_recovery_remaining_time(recovery_from, recovery_until)

        if hours_to_valid != None and remaining_hours != None:
            if hours_to_valid < 0:
                level = 3
                remaining_days = output.get_not_yet_valid(-hours_to_valid)
                expired = True
            elif remaining_hours <= 0:
                level = 3
                remaining_days = output.get_expired(remaining_hours)
                expired = True
            elif remaining_hours * 24 < 14:
                level = 2
                remaining_hours = output.get_hours_left(remaining_hours)
                remaining_days = remaining_hours
                expired = False
            else:
                level = 1
                remaining_days = output.get_months_left(remaining_hours)
                expired = False

            output.add_remaining_time(certificate_type, certdate, level, remaining_days)
        key = cup.get_key_coseobj(gpp.get_kid())
        gpp.set_key(key)
        verified = gpp.verify()

        if verified:
            output.add_general_info_ok(k.get_verified()[1], verified)
        else:
            output.add_general_info_error(k.get_verified()[1], verified)

        unknown_cert = gpp.certificate_type not in (
                k.get_vaccine()[0],
                k.get_test()[0],
                k.get_recovery()[0]
        )

        valid = verified and not expired and not positive and not unknown_cert
        return valid

