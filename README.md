# Green Pass Verifier

![A verified green pass](https://github.com/berdav/greenpass/blob/master/img/draghi.png?raw=true)

Scriptable green pass verifier.
With this application you can automatize accesses based on green pass validity.
It can also be used to analyze your digital certification (e.g. to print
which key was used to sign the certificate, `--verbose`).

It is compatibile with EU certificates (DGC) and UK certificate (NHS).

## Installation
You need to have pip and libzbar to install the application.

You can install it using your favorite package manager, for instance in Ubuntu:

```bash
sudo apt install python3-pip libzbar0
```

You can just install the application using pip:
```bash
pip install greenpass
```

If you want to install it from sources, install the python3 requirements
using the following command:
```bash
pip3 install -r requirements.txt
```

## Usage
You can feed the application with different file formats, for instance:

Green pass official PDFs
```bash
greenpass --pdf greenpass.pdf
```

QRCode images in PNG
```bash
greenpass --qr greenpass.png
```

Txt files with the content of the qrcode
```bash
greenpass --txt greenpass.txt
```

Standard input and pipes
```bash
zbarimg --raw greenpass.png | greenpass --txt -
```

On a side note, you can verify camera-acquired images if your scanner
prints the raw content of the QRcode on stdout
```bash
zbarcam --raw -q1 | greenpass --txt -
```

The application returns an UNIX compatible code, therefore you can
concatenate commands that will be executed only if the green pass is
verified.
```bash
greenpass --qr greenpass.png && echo "green pass ok"
```

You can also get the expiration configuration using `--settings` without
other inputs.
```bash
greenpass --settings
```
![Settings screen](https://github.com/berdav/greenpass/blob/master/img/settings.png?raw=true)

## Switches
```bash
-h --help
```
Help, print the help message

You need to use one of:

```bash
--settings
```
Dump the settings used by the Italian application

```bash
--qr QR
```
Analyze the qrcode QR

```bash
--pdf PDF
```
Analyze the pdf file PDF

```bash
--txt TXT
```
Analyze the txt file TXT

Caching options:
```bash
--cachedir CACHEDIR
```
Use CACHEDIR as the cache directory, by default the cache is placed in `$HOME/.local/greenpass`.

Miscellaneous switches: 
```bash
--raw
```
Print the raw content (JSON) of the certificate

```bash
--no-color
```
Disable colored output.

```bash
--no-cache
```
Disable cache, redownload everything.

```bash
--key KEY
```
Use the content of the file KEY as the public certificate (DGC) or the public key (NHS) to
verify the certificate.

```bash
--verbose
```
Print more information (e.g. which key verifies the certificate).

## Pointers
If you want more information on the green pass certification and how
to parse or verify it you can refer to the following resources:

[Greenpass Encoding documentation](https://github.com/ehn-dcc-development/hcert-spec)

[Official Italian Android application](https://github.com/ministero-salute/it-dgc-verificaC19-android )

[JSON schema and specifications](https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf)

[A very detailed blog post on how decode the pass](https://gir.st/blog/greenpass.html)
