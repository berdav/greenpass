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

You can also use it through the pre-built Docker image, you can find it
[here](https://hub.docker.com/r/berdav/greenpass).  You can easily use
it using:
```bash
sudo docker run --rm -ti berdav/greenpass --settings
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

Debug the cryptographic part of your greenpass
```bash
greenpass --qr greenpass.png --dump-sign
```

Print the key which the greenpass was signed with
```bash
greenpass --qr greenpass.png --verbose --no-cache
```

Check if a greenpass was valid or will be valid on a certain date
```bash
greenpass --qr greenpass.png --at-date '2021-10-30 18:34'
```

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
Disable cache, download everything without saving it.

```bash
--clear-cache
```
Redownload the entire cache, useful to update settings.

```bash
--key KEY
```
Use the content of the file KEY as the public certificate (DGC) or the public key (NHS) to
verify the certificate.

```bash
--verbose
```
Print more information (e.g. which key verifies the certificate).

```bash
--dump-sign
```
Print details on the headers and signature of the certificate.

```bash
--at-date AT_DATE 
```
Use AT_DATE instead of the current date

```bash
--recovery-expiration
```
The recovery certification contains an expiration date.  By
default this date is ignored, this switch re-enables the check
and consider this date (in addition to the settings date).


## Docker Container
The docker image shipped with the program can be used in the following
way:

```bash
zbarimg --raw qrcode.png | sudo docker -i greenpass
```
Read a PNG greenpass qrcode

```bash
sudo docker -i greenpass --settings
```
To read the settings

And virtually with all the switches you can find in the previous
section.  At the moment, files are not easily passed in the container,
therefore it is better to process the qrcode or the pdf outside of the
container and extract the qrcode text to pass in the application.

## Pointers
If you want more information on the green pass certification and how
to parse or verify it you can refer to the following resources:

[Greenpass Encoding documentation](https://github.com/ehn-dcc-development/hcert-spec)

[Official Italian Android application](https://github.com/ministero-salute/it-dgc-verificaC19-android )

[JSON schema and specifications](https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf)

[A very detailed blog post on how decode the pass](https://gir.st/blog/greenpass.html)
