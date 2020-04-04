#!/bin/bash

BASE_TRANSFORMER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BASE_TRANSFORMER")
REPO=$(dirname "$TRANSFORMERS")

cd $BASE_TRANSFORMER

MOSES=$TRANSFORMERS/software/mosesdecoder
SUBWORD_NMT=$TRANSFORMERS/software/subword-nmt

DATA=$REPO/data
OUT_TXT=$BASE_TRANSFORMER/data-txt
OUT_BIN=$BASE_TRANSFORMER/data-bin
LOGS=$BASE_TRANSFORMER/logs

mkdir -p $OUT_TXT $OUT_BIN $LOGS

if [ ! -d "$MOSES" ]; then
    git clone https://github.com/moses-smt/mosesdecoder.git $MOSES
fi
if [ ! -d "$SUBWORD_NMT" ]; then
    git clone https://github.com/rsennrich/subword-nmt.git $SUBWORD_NMT
fi

module load generic
sbatch -D $BASE_TRANSFORMER -o $LOGS/slurm-%j-prepare-de-ls-data.out \
    $BASE_TRANSFORMER/job-prepare-de-ls-data.sh $REPO
