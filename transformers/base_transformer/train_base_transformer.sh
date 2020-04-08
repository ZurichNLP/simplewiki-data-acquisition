#!/bin/bash

BASE_TRANSFORMER="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BASE_TRANSFORMER")
REPO=$(dirname "$TRANSFORMERS")

cd $BASE_TRANSFORMER

DATA_BIN=$BASE_TRANSFORMER/data-bin
LOGS=$BASE_TRANSFORMER/logs

CHECKPOINT_DIR=$BASE_TRANSFORMER/checkpoints/checkpoints_de_ls_base_transformer
mkdir -p $CHECKPOINT_DIR

module load volta cuda/10.0
sbatch -D $BASE_TRANSFORMER -o $LOGS/slurm-%j-train-base-transformer.out \
    $BASE_TRANSFORMER/job-train-base-transformer.sh $REPO
