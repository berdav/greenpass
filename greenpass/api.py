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
import base64
import requests
from OpenSSL import crypto
from binascii import hexlify
from bs4 import BeautifulSoup
from cose.keys import EC2Key, CoseKey

from greenpass.URLs import *

# Update certificate signer
class CertificateUpdater(object):
    def __init__(self):
        self.verbose = False

    def set_verbose(self):
        self.verbose = True

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
                out = i
            if _type == "nhs":
                targetkid = hexlify(base64.b64decode(x["kid"]))
                out = targetkid
            if targetkid == hexkid:
                return (_type, out)
            i += 1
        return (_type, -1)

    # Dispatch to correct Key IDX retrieve function
    def get_kid_idx(self, kid):
        k = self._get_kid_idx(kid, "nhs")
        if k[1] != -1:
            return k
        k = self._get_kid_idx(kid, "dgc")
        if self.verbose:
            print("[ ] Kid: {} idx: {}".format(base64.b64encode(kid), k[1]))

        if k[1] != -1:
            return k

        print("[-] Could not find certification authority")
        sys.exit(1)

    # Get key from DGC style repository
    def get_key_dgc(self, idx):
        certificate = None
        r = requests.get("{}".format(BASE_URL_DGCG))
        if r.status_code != 200:
            print("[-] Error from API")
            sys.exit(1)

        soup = BeautifulSoup(r.text, 'html.parser')
        trust_list_json = soup.find("code", {"id": "trust-list-json"})
        trust_list = json.loads(trust_list_json.string)
        target = base64.b64encode(idx).decode()
        for country in trust_list["dsc_trust_list"].values():
            for el in country["keys"]:
                if el["kid"] == target:
                    certificate = base64.b64decode(el["x5c"][0])
                    break

        return certificate

    # Return public key
    def loadpubkey(self, certificate):
        # Load certificate and dump the pubkey
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, certificate)

        if self.verbose:
            subject = ' '.join(map(lambda x: x[1].decode(), x509.get_subject().get_components()))
            print("[ ] Signed with public key from")
            print("    {}".format(subject))
        pubkey = crypto.dump_publickey(crypto.FILETYPE_ASN1, x509.get_pubkey())
        return pubkey

    def extractpubkey(self, pubkey):
        return pubkey[26::]

    # Get key from NHS style repository
    def get_key_nhs(self, idx):
        r = requests.get("{}/pubkeys/keys.json".format(BASE_URL_NHS))
        for x in json.loads(r.text):
            targetkid = hexlify(base64.b64decode(x["kid"]))

            if targetkid == idx:
                return base64.b64decode(x["publicKey"])

    # Retrieve key from remote repository
    def get_key(self, kid):
        keytype, idx = self.get_kid_idx(kid)

        if keytype == "nhs":
            pubkey = self.get_key_nhs(idx)
            pubkey = self.extractpubkey(pubkey)
        elif keytype == "dgc":
            certificate = self.get_key_dgc(kid)
            pubkey = self.loadpubkey(certificate)
            pubkey = self.extractpubkey(pubkey)

        return pubkey

    # Retrieve key and convert to coseobj
    def get_key_coseobj(self, kid):
        pubkey = self.get_key(kid)
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
        super(CachedCertificateUpdater, self).__init__()

    def get_key(self, kid):
        # Replace / with a value that cannot be found in base64
        enckid = base64.b64encode(kid).decode().replace("/", ".")
        cachepath = os.path.join(self.cachedir, enckid)
        superclass = super(CachedCertificateUpdater, self)

        if not os.path.exists(cachepath):
            with open(cachepath, "wb") as f:
                f.write(superclass.get_key(kid))

        with open(cachepath, "rb") as f:
            keybytes = f.read()

        return keybytes

class ForcedCertificateUpdater(CertificateUpdater):
    def __init__(self, path):
        self.keypath = path
        super(ForcedCertificateUpdater, self).__init__()

    def get_key(self, _kid):
        with open(self.keypath, "rb") as f:
            keybytes = f.read()

        return keybytes
