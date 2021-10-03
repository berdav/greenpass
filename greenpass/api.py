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

import os
import sys
import json
import base64
import requests
from OpenSSL import crypto
from binascii import hexlify
from cose.keys import EC2Key, CoseKey

from greenpass.URLs import *

# Update certificate signer
class CertificateUpdater(object):
    def __init__(self):
        pass

    # Get KEY index from online status page
    def _get_kid_idx(self, kid, _type="dgc"):
        if _type == "dgc":
            r = requests.get("{}/signercertificate/status".format(BASE_URL_DGC))
        elif _type == "nhs":
            r = requests.get("{}/pubkeys/keys.json".format(BASE_URL_NHS))
        else:
            return ("unk", -1)
        if r.status_code != 200:
            print("[-] Error from API")
            sys.exit(1)
        i = 0
        hexkid = hexlify(kid)
        for x in json.loads(r.text):
            if _type == "dgc":
                targetkid = hexlify(base64.b64decode(x))
            if _type == "nhs":
                targetkid = hexlify(base64.b64decode(x["kid"]))
            if targetkid == hexkid:
                return (_type, i)
            i += 1
        return (_type, -1)

    # Dispatch to correct Key IDX retrieve function
    def get_kid_idx(self, kid):
        k = self._get_kid_idx(kid, "nhs")
        if k[1] != -1:
            return k
        k = self._get_kid_idx(kid, "dgc")
        if k[1] != -1:
            return k

        print("[-] Could not find certification authority")
        sys.exit(1)

    # Get key from DGC style repository
    def get_key_dgc(self, idx):
        headers = { "x-resume-token": str(idx) }
        r = requests.get("{}/signercertificate/update".format(BASE_URL_DGC), headers=headers)
        if r.status_code != 200:
            print("[-] Error from API")
            sys.exit(1)

        certificate = base64.b64decode(r.text)
        return certificate

    # Return public key
    def loadpubkey(self, certificate):
        # Load certificate and dump the pubkey
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, certificate)
        pubkey = crypto.dump_publickey(crypto.FILETYPE_ASN1, x509.get_pubkey())[26::]
        return pubkey

    # Get key from NHS style repository
    def get_key_nhs(self, idx):
        r = requests.get("{}/pubkeys/keys.json".format(BASE_URL_NHS))
        for x in json.loads(r.text):
            targetkid = hexlify(base64.b64decode(x["kid"]))
            if targetkid == hexkid:
                return base64.b64decode(x["publicKey"])

    # Retrieve key from remote repository
    def get_key(self, kid):
        keytype, idx = self.get_kid_idx(kid)

        if keytype == "dgc":
            pubkey = self.get_key_dgc(idx)
        elif keytype == "nhs":
            pubkey = self.get_key_nhs(idx)
        return pubkey

    # Retrieve key and convert to coseobj
    def get_key_coseobj(self, kid):
        certificate = self.get_key(kid)
        pubkey = self.loadpubkey(certificate)
        return self.getcoseobj(pubkey)

    # Return COSE object from public key
    def getcoseobj(self, pubkey):
        # X is the first 32 bits, Y are the remaining ones
        x = pubkey[1:int(len(pubkey)/2) + 1]
        y = pubkey[int(len(pubkey)/2) + 1::]

        # Create COSE key
        kattr = {
                "KTY":   "EC2",
                "CURVE": "P_256",
                "ALG":   "ES256",
                "X":     x,
                "Y":     y
        }
        return CoseKey.from_dict(kattr)

# Cached version of Certificate Updater,
#  saves and retrieves public keys using a cache directory
class CachedCertificateUpdater(CertificateUpdater):
    def __init__(self, cachedir):
        self.cachedir = cachedir
        os.makedirs(cachedir, exist_ok=True)

    def get_key(self, kid):
        enckid = base64.b64encode(kid).decode()
        cachepath = os.path.join(self.cachedir, enckid)
        superclass = super(CachedCertificateUpdater, self)

        if not os.path.exists(cachepath):
            with open(cachepath, "wb") as f:
                f.write(superclass.get_key(kid))

        with open(cachepath, "rb") as f:
            keybytes = f.read()

        return keybytes

