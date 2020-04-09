#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

LOGS=$BACKTRANSLATION/logs

CHECKPOINT_DIR=$BACKTRANSLATION/checkpoints/checkpoints_de_ls_para_plus_bt
mkdir -p $CHECKPOINT_DIR

module load volta cuda/10.0
sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-train-bt-model.out \
    $BACKTRANSLATION/job-train-bt-model.sh $REPO
