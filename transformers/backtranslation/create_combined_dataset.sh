#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

LOGS=$BACKTRANSLATION/logs

BT_OUT=$BACKTRANSLATION/generation/backtranslations
BT_TXT=$BACKTRANSLATION/data-txt/simplewiki_ls_bt
BT_BIN=$BACKTRANSLATION/data-bin/simplewiki_ls_bt
COMBINED=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para_plus_bt

mkdir -p $BT_TXT $BT_BIN $COMBINED

module load generic
sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-create-combined-dataset.out \
    $BACKTRANSLATION/job-create-combined-dataset.sh $REPO
