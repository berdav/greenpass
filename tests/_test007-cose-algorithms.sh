#!/bin/bash

set -eu

GPFILE_AH="tests/data/ah-1900.txt"
GPFILE_SQ="tests/data/sq-1900.txt"

# Dump sign check
assert_string_out "Ps256" "$GP" --txt "$GPFILE_SQ" --dump-sign
assert_string_out "Es256" "$GP" --txt "$GPFILE_AH" --dump-sign

# Verify the certificates
assert_true "$GP" --txt "$GPFILE_SQ" --no-block-list
assert_true "$GP" --txt "$GPFILE_AH" --no-block-list
