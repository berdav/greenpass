#!/bin/bash

set -eu

CACHEDIR="/tmp/gp-cache"
# CNAM certification authority
GPFILE_AH="tests/data/ah-1900.png"
# No certification authority
GPFILE_MF="tests/data/musterfrau.png"
# German certification authority
GPFILE_RK="tests/data/rk.png"

assert_file_exists "$GPFILE_AH"
assert_file_exists "$GPFILE_MF"

rm -rf "$CACHEDIR"
assert_false $GP --cachedir "$CACHEDIR" --settings
assert_file_exists "$CACHEDIR/settings"

# Download the keys in the cache
assert_true  $GP --cachedir "$CACHEDIR" --qr "$GPFILE_AH" --no-block-list
assert_file_exists "$CACHEDIR/53FOjX.4aJs="
# This is not signed by a real authority
assert_false $GP --cachedir "$CACHEDIR" --qr "$GPFILE_MF"
# German certification authority
assert_true  $GP --cachedir "$CACHEDIR" --qr "$GPFILE_RK" --no-block-list
assert_file_exists "$CACHEDIR/XkVWZqUeeFc="

assert_file_exists "$CACHEDIR/tests"
