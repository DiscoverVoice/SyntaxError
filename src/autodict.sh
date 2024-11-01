#!/bin/bash

QLDIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")/utils/autodict_ql"
WORKDIR=$PWD
codeql database create temp-db --language=cpp --command='bash -c "make clean && make"' --overwrite
codeql database upgrade $WORKDIR/temp-db
cd $QLDIR
python3 autodict-ql.py $QLDIR $WORKDIR/temp-db $WORKDIR/tokens
