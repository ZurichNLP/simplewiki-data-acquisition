#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --gres=gpu:Tesla-V100:1
#SBATCH --qos=vesta
#SBATCH --partition=volta

# calling script needs to set:
# $REPO
# $CHUNK

REPO=$1
CHUNK=$2

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

BT_OUT=$BACKTRANSLATION/generation/backtranslations
CHECKPOINT_DIR=$BACKTRANSLATION/checkpoints/checkpoints_ls_de_reverse_model
DATA_BIN=$BACKTRANSLATION/data-bin

fairseq-generate $DATA_BIN/simplewiki_ls_mono/chunk${CHUNK} \
    --path $CHECKPOINT_DIR/checkpoint_best.pt \
    --skip-invalid-size-inputs-valid-test \
    --max-tokens 4096 \
    --beam 5 \
> $BT_OUT/bt.chunk${CHUNK}.out
