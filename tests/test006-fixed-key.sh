#!/bin/bash

set -eu

GPFILE_AH="tests/data/ah-1900.png"
GPFILE_RK="tests/data/rk.png"
CACHEDIR="/tmp/gp-cache"

# Download the MF key
assert_true $GP --qr "$GPFILE_AH" --no-block-list --cachedir "$CACHEDIR"
# Download the RK key
assert_true $GP --qr "$GPFILE_RK" --no-block-list --cachedir "$CACHEDIR"

# Correct key validation
assert_true  $GP --qr "$GPFILE_AH" --no-block-list --cachedir "$CACHEDIR" --key "$CACHEDIR/53FOjX.4aJs="
# Incorrect key validation
assert_false $GP --qr "$GPFILE_AH" --no-block-list --cachedir "$CACHEDIR" --key "$CACHEDIR/XkVWZqUeeFc="

