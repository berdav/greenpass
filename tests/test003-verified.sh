#!/bin/bash

set -eu

assert_file_exists "tests/data/ah-1900.txt"
assert_string_out "Verified.*True" "$GP" --language en --txt "tests/data/ah-1900.txt"
# Without the blocklist the certificate is valid
assert_true "$GP" --txt "tests/data/ah-1900.txt" --no-block-list
