#!/bin/bash

set -eu

WARN="This certificate can generate problems with base45 decoders"
F=tests/data/ah-1900.txt
D="/tmp/ah-1900.txt"

# Original
cp "$F" "$D.orig"
# Modified
cp "$F" "$D.mod"
echo "" >> "$D.mod"

# QR Code original
qrencode -o "$D.orig.png" -r "$D.orig"
qrencode -o "$D.mod.png" -r "$D.mod"


assert_file_exists "$D.mod"
assert_file_exists "$D.orig"
assert_file_exists "$D.mod.png"
assert_file_exists "$D.orig.png"

"$GP" --txt "$D.mod" | grep "$WARN" 
if "$GP" --txt "$D.orig" | grep "$WARN" ; then
	exit 1
fi

"$GP" --qr "$D.mod.png" | grep "$WARN" 
if "$GP" --qr "$D.orig.png" | grep "$WARN" ; then
	exit 1
fi

