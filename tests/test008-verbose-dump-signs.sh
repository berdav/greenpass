#!/bin/bash

set -eu

assert_file_exists tests/data/ah-1900.txt
assert_false "$GP" --txt tests/data/ah-1900.txt --dump-sign
assert_string_out "Es256" "$GP" --txt tests/data/ah-1900.txt --dump-sign

assert_string_out "FR CNAM 180035024 DSC_FR_023" "$GP" --txt tests/data/ah-1900.txt --verbose --no-block-list
