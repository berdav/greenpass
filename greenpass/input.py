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

