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

import io
import sys
import fitz
from PIL import Image
from pyzbar import pyzbar

# Class to get input data from various sources.
# Current supported:
# TXT Data
# PNG Image
# PDF Documents
class InputTransformer(object):
    def __init__(self, path, filetype):
        if filetype == "txt":
            if path == "-":
                outdata = bytes(sys.stdin.read().split("\n")[0].encode("ASCII"))
            else:
                with open(path, 'rb') as f:
                    outdata = f.read()
        else:
            if filetype == "png":
                img = Image.open(path)
            elif filetype == "pdf":
                # Convert PDF to JPG
                pdf_file = fitz.open(path)
                imagebytes = pdf_file.extractImage(6)["image"]
                img = Image.open(io.BytesIO(imagebytes))
            else:
                print("[-] file format {} not recognized".format(filetype), file=sys.stderr)

            decoded = pyzbar.decode(img)
            if len(decoded) < 1:
                print("[-] Value not found", file=sys.stderr)
                sys.exit(1)
            output = decoded[0]
            if output.type != "QRCODE":
                print("[-] Not a qrcode", file=sys.stderr)
                sys.exit(1)

            outdata = output.data
        self.data = outdata

    def get_data(self):
        return self.data

