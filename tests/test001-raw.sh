#!/bin/bash

set -eu

assert_file_exists tests/data/ah-1900.txt
assert_false "$GP" --raw --txt tests/data/ah-1900.txt
assert_string_out "URN:UVCI:01:FR:T5DWTJYS4ZR8#4" "$GP" --raw --txt tests/data/ah-1900.txt

assert_file_exists tests/data/ah-1900.png
assert_false "$GP" --raw --qr  tests/data/ah-1900.png
assert_string_out "URN:UVCI:01:FR:T5DWTJYS4ZR8#4" "$GP" --raw --qr tests/data/ah-1900.png
