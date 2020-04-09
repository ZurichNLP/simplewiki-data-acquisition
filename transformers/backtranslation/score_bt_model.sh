#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

GENERATION_OUT=$BACKTRANSLATION/generation/bt_model

mkdir -p $GENERATION_OUT

MOSES=$TRANSFORMERS/software/mosesdecoder
LOGS=$BACKTRANSLATION/logs

if [ ! -d "$MOSES" ]; then
    git clone https://github.com/moses-smt/mosesdecoder.git $MOSES
fi

module load volta cuda/10.0
sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-score-bt-model.out \
    $BACKTRANSLATION/job-score-bt-model.sh $REPO
