#!/bin/sh

set -eu

NEXT_VER="${1:-newversion}"

get_current_version() {
  git tag --list | sort -V | tail -1 | sed 's/^v//g'
}

increment() {
  echo "$1" | awk -F. -v OFS=. '{$NF++;print}'
}

release() {
  sed -i \
    "s#\(version[\t ]*=[\t ]*'\)[0-9]\+\.[0-9]\+\.[0-9]\+#\1$1#" \
    setup.py
  sed -i \
    "s#\(download_url[\t ].*/v\)[0-9]\+\.[0-9]\+\.[0-9]\+\.zip'#\1$1.zip'#" \
    setup.py
}

if test "x$NEXT_VER" = "xnewversion"; then
  NEXT_VER="$(increment $(get_current_version))"
fi

release "$NEXT_VER"
git status
git add setup.py
git commit -m "v$NEXT_VER release"
git tag "v$NEXT_VER"
