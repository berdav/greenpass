#!/bin/bash

set -eu

assert_file_exists tests/data/ah-1900.txt
assert_true "$GP" --txt tests/data/ah-1900.txt --no-block-list
assert_true "$GP" --txt tests/data/ah-1900.txt --batch --no-block-list
