#!/bin/bash

set -eu

assert_file_exists tests/data/ah-1900.txt
assert_string_out "Vaccine" "$GP" --language en --txt tests/data/ah-1900.txt
assert_string_out "Vaccino" "$GP" --language it --txt tests/data/ah-1900.txt
assert_string_out "Impfung" "$GP" --language de --txt tests/data/ah-1900.txt
