#!/bin/bash

set -eu

assert_file_exists "tests/data/ah-1900.txt"
# The AH certificate is blocked by the blocklist
assert_false "$GP" --txt "tests/data/ah-1900.txt"
assert_string_out "Blocklisted.*True" "$GP" --txt "tests/data/ah-1900.txt"
