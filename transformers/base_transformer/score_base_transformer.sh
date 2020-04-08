#!/bin/bash

BASE_TRANSFORMER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BASE_TRANSFORMER")
REPO=$(dirname "$TRANSFORMERS")

cd $BASE_TRANSFORMER

mkdir -p $BASE_TRANSFORMER/generation

MOSES=$TRANSFORMERS/software/mosesdecoder
LOGS=$BASE_TRANSFORMER/logs

if [ ! -d "$MOSES" ]; then
    git clone https://github.com/moses-smt/mosesdecoder.git $MOSES
fi

module load volta cuda/10.0
sbatch -D $BASE_TRANSFORMER -o $LOGS/slurm-%j-score-base-transformer.out \
    $BASE_TRANSFORMER/job-score-base-transformer.sh $REPO
