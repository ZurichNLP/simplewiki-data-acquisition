#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

DATA_BIN=$BACKTRANSLATION/data-bin
LOGS=$BACKTRANSLATION/logs

CHECKPOINT_DIR=$BACKTRANSLATION/checkpoints/checkpoints_ls_de_reverse_model
mkdir -p $CHECKPOINT_DIR

module load volta cuda/10.0
sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-train-reverse-model.out \
    $BACKTRANSLATION/job-train-reverse-model.sh $REPO
