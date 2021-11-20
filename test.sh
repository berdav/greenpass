#!/bin/bash

GP="./greenpass.py"
DEBUG="${1:-false}"
OUT=/dev/null
if test "x$DEBUG" = "xtrue"; then
	OUT=/dev/stdout
fi
if test "x$DEBUG" = "xcoverage"; then
	GP="tools/coverage.sh"
	OUT=/dev/stdout
	python3-coverage erase
fi
export OUT
export GP
shift

set -eu

assert_false() {
	echo "Asserting $@ == false" >"$OUT"

	set +e
	$@ >"$OUT" 2>"$OUT"
	R="$?"
	set -e

	echo "Returned $R" >"$OUT"
	test "$R" != 0
}
export -f assert_false

assert_true() {
	echo "Asserting $@ == true" >"$OUT"
	$@ >"$OUT" 2>"$OUT"
	R="$?"
	echo "Returned $R" >"$OUT"
	return "$R"
}
export -f assert_true

assert_string_out() {
	S="$1"
	shift
	echo "Asserting '$S' in $@" >"$OUT"
	$@ 2>"$OUT" | grep "$S" >"$OUT"
}
export -f assert_string_out

assert_file_exists() {
	echo "Asserting $1 file exists" >"$OUT"
	ls "$1" >"$OUT" 2>"$OUT"
}
export -f assert_file_exists

error_exit() {
	echo "[x] Test $1 Failed!"
	exit 1
}

echo "Running testsuite"
if test $# -gt 0; then
	TESTS=( $@ )
else
	echo "Executing all tests"
	TESTS=( $(ls -1 tests/test*) )
fi
for t in ${TESTS[@]}; do
	echo "Executing $t"
	"$t" || error_exit "$t"
done
echo "All tests passed"
