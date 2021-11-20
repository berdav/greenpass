#!/bin/sh

python3-coverage run -a \
    --omit="*/dist-packages/*,*/site-packages/*" \
    ./greenpass.py $@
