# Green Pass Verifier

![A verified green pass](https://github.com/berdav/greenpass/blob/master/img/draghi.png?raw=true)

Scriptable green pass verifier.
With this application you can automatize accesses based on green pass validity.

## Installation
You need to have pip and libzbar to install the application.

You can install it using your favorite package manager, for instance in Ubuntu:

```bash
$ sudo apt install python3-pip libzbar0
```

You can just install the application using pip:
```bash
$ pip install greenpass
```

If you want to install it from sources, install the python3 requirements
using the following command:
```bash
$ pip3 install -r requirements.txt
```

## Usage
You can feed the application with different file formats, for instance:

Green pass official PDFs
```bash
$ greenpass --pdf greenpass.pdf
```

QRCode images in PNG
```bash
$ greenpass --qr greenpass.png
```

Txt files with the content of the qrcode
```bash
$ greenpass --txt greenpass.txt
```

Standard input and pipes
```bash
$ zbarimg --raw greenpass.png | greenpass --txt -
```

The application returns an UNIX compatible code, therefore you can
concatenate commands that will be executed only if the green pass is
verified
```bash
$ greenpass --qr greenpass.png && echo "green pass ok"
```

You can also get the expiration configuration using `--settings` without
other inputs.
```bash
$ greenpass --settings
```
![Settings screen](https://github.com/berdav/greenpass/blob/master/img/settings.png?raw=true)
