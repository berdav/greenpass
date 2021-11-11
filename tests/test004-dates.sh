#!/bin/bash

set -eu

assert_file_exists "tests/data/ah-1900.txt"

CHECK_CMD="$GP --txt "tests/data/ah-1900.txt" --no-block-list"

# Without the blocklist the certificate is valid at 2021-10-30 11:43
# Only date
assert_true "$CHECK_CMD" --at-date '2021-10-30'
# Date and time
assert_true "$CHECK_CMD" --at-date '2021-10-30-11:43'
# Date and time and seconds
assert_true "$CHECK_CMD" --at-date '2021-10-30-11:43:10'
# Date and time and timezone
assert_true "$CHECK_CMD" --at-date '2021-10-30-11:43+0200'
# Date and time and seconds and timezone
assert_true "$CHECK_CMD" --at-date '2021-10-30-11:43:10+0200'

# Even without blocklist, the certificate is invalid at 2022-10-01 11:43
assert_false "$CHECK_CMD" --at-date '2022-10-01'
assert_false "$CHECK_CMD" --at-date '2022-10-01-11:43'
assert_false "$CHECK_CMD" --at-date '2022-10-01-11:43:10'
assert_false "$CHECK_CMD" --at-date '2022-10-01-11:43+0200'
assert_false "$CHECK_CMD" --at-date '2022-10-01-11:43:10+0200'

# Even without blocklist, the certificate was invalid before 2021-10-01 00:00
assert_false "$CHECK_CMD" --at-date '2021-09-30'
assert_false "$CHECK_CMD" --at-date '2021-09-30-11:43'
assert_false "$CHECK_CMD" --at-date '2021-09-30-11:43:10'
assert_false "$CHECK_CMD" --at-date '2021-09-30-11:43+0200'
assert_false "$CHECK_CMD" --at-date '2021-09-30-11:43:10+0200'
