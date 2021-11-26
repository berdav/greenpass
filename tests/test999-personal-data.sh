#!/bin/bash

set -eu

TESTDIR="tests/data/private/test"
VACCINEDIR="tests/data/private/vaccine"
RECOVERYDIR="tests/data/private/recovery"

get_date() {
	T="$1"
	shift
	"$GP" $@ --language en --no-color |
		awk "/$T/{printf(\"%sT%s\\n\", \$3, \$4)}" ||
		true
}

date_evaluate() {
	date -d "$1" "+%Y-%m-%dT%H:%M:%S%:z"
}

vaccine_test() {
	TYPE="$1"
	FILE="$2"
	L="$3"
	# Retrieve the vaccination date
	D="$(get_date "Vaccine Date" "--$TYPE" "$FILE")"

	# Two weeks after, the vaccine shall be valid
	N="$(date_evaluate "$D + 15 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
		--at-date "$N"              \
		--no-block-list             \
		--language "$L"

	# The day before, the vaccine shall not be valid
	N="$(date_evaluate "$D - 1 day" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
		--at-date "$N"               \
		--no-block-list              \
		--language "$L"

	# The year after, the vaccine shall not be valid
	N="$(date_evaluate "$D + 1 year" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
		--at-date "$N"               \
		--no-block-list              \
		--language "$L"

	# A week before the year, the vaccine shall be valid (if it is a
	# complete one)
	N="$(date_evaluate "$D - 15 day + 1 year" | sed 's/T/-/g')"
	if "$GP" "--$TYPE" "$FILE" --no-color | grep Doses | grep -q '2/2'; then
		assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"              \
			--no-block-list             \
			--language "$L"
	fi
}

test_test() {
	TYPE="$1"
	FILE="$2"
	L="$3"
	# Retrieve the vaccination date
	D="$(get_date "Test Date" "--$TYPE" "$FILE")"

	# The day after, the test shall be valid
	N="$(date_evaluate "$D + 1 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# The day before, the test shall not be valid
	N="$(date_evaluate "$D - 1 day" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# Two days after, the test shall not be valid
	N="$(date_evaluate "$D + 2 days" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"
}

recovery_test() {
	TYPE="$1"
	FILE="$2"
	L="$3"
	# Retrieve the start date
	D="$(get_date "Recovery Date" "--$TYPE" "$FILE")"

	# The day after, the recovery shall be valid
	N="$(date_evaluate "$D + 1 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# Try also with cache
	N="$(date_evaluate "$D + 1 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# And clearing the cache
	N="$(date_evaluate "$D + 1 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# The day before, the recovery shall not be valid
	N="$(date_evaluate "$D - 1 day" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"       \
			--no-block-list      \
			--language "$L"

	# By default the old recovery included an expiration date.
	# This is ignored by the current verification apps
	E="$(get_date "Validity Until" "--$TYPE" "$FILE")"
	N="$(date_evaluate "$E + 1 day" | sed 's/T/-/g')"
	assert_true "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"      \
			--no-block-list     \
			--language "$L"

	# Also re-enable the check to see if the expiration date
	# is correctly considered.
	assert_false "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"       \
			--no-block-list      \
			--language "$L"      \
			--recovery-expiration

	# 6 months after, the recovery shall not be valid
	N="$(date_evaluate "$D + 6 months" | sed 's/T/-/g')"
	assert_false "$GP" "--$TYPE" "$FILE" \
			--at-date "$N"       \
			--no-block-list      \
			--language "$L"
}

PDFS=( "$(ls -1 "$VACCINEDIR/"*.pdf 2>/dev/null || true)" )
PNGS=( "$(ls -1 "$VACCINEDIR/"*.{png,jpg} 2>/dev/null || true)" )
TXTS=( "$(ls -1 "$VACCINEDIR/"*.txt 2>/dev/null || true)" )
# Vaccine test
for language in it en de ; do
	for PDF in ${PDFS[@]}; do
		vaccine_test "pdf" "$PDF" "$language"
	done
	for PNG in ${PNGS[@]}; do
		vaccine_test "qr" "$PNG" "$language"
	done
	for TXT in ${TXTS[@]}; do
		vaccine_test "txt" "$TXT" "$language"
	done
done

PDFS=( "$(ls -1 "$RECOVERYDIR/"*.pdf 2>/dev/null || true)" )
PNGS=( "$(ls -1 "$RECOVERYDIR/"*.{png,jpg} 2>/dev/null || true)" )
TXTS=( "$(ls -1 "$RECOVERYDIR/"*.txt 2>/dev/null || true)" )
# Recovery test
for language in it en de ; do
	for PDF in ${PDFS[@]}; do
		recovery_test "pdf" "$PDF" "$language"
	done
	for PNG in ${PNGS[@]}; do
		recovery_test "qr" "$PNG" "$language"
	done
	for TXT in ${TXTS[@]}; do
		recovery_test "txt" "$TXT" "$language"
	done
done

PDFS=( "$(ls -1 "$TESTDIR/"*.pdf 2>/dev/null || true)" )
PNGS=( "$(ls -1 "$TESTDIR/"*.{png,jpg} 2>/dev/null || true)" )
TXTS=( "$(ls -1 "$TESTDIR/"*.txt 2>/dev/null || true)" )
# Test test (duh!)
for language in it en de; do
	for PDF in ${PDFS[@]}; do
		test_test "pdf" "$PDF" "$language"
	done
	for PNG in ${PNGS[@]}; do
		test_test "qr" "$PNG" "$language"
	done
	for TXT in ${TXTS[@]}; do
		test_test "txt" "$TXT" "$language"
	done
done
