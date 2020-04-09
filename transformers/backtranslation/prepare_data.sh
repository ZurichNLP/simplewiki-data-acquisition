#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

MOSES=$TRANSFORMERS/software/mosesdecoder
SUBWORD_NMT=$TRANSFORMERS/software/subword-nmt

if [ ! -d "$MOSES" ]; then
    git clone https://github.com/moses-smt/mosesdecoder.git $MOSES
fi
if [ ! -d "$SUBWORD_NMT" ]; then
    git clone https://github.com/rsennrich/subword-nmt.git $SUBWORD_NMT
fi

DATA=$REPO/data
LOGS=$BACKTRANSLATION/logs

mkdir -p $LOGS

# preprocessing parallel data

OUT_TXT=$BACKTRANSLATION/data-txt/simplewiki_de_ls_para
OUT_BIN=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para

mkdir -p $OUT_TXT $OUT_BIN

module load generic
PARA_PREP=$(sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-prepare-de-ls-data.out \
    $BACKTRANSLATION/job-prepare-de-ls-data.sh $REPO \
| tee /dev/tty \
| grep -Po "[0-9]+$")

# preprocessing unaligned/monolingual data

OUT_TXT=$BACKTRANSLATION/data-txt/simplewiki_ls_mono
OUT_BIN=$BACKTRANSLATION/data-bin/simplewiki_ls_mono

mkdir -p $OUT_TXT $OUT_BIN

sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-prepare-monolingual-data.out \
    --dependency=afterok:$PARA_PREP \
    $BACKTRANSLATION/job-prepare-monolingual-data.sh $REPO
