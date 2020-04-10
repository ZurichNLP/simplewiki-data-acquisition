#!/bin/bash
#SBATCH --time=72:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --gres=gpu:Tesla-V100:1
#SBATCH --qos=vesta
#SBATCH --partition=volta

# calling script needs to set:
# $REPO

REPO=$1

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

DATA_BIN=$BACKTRANSLATION/data-bin
COMBINED=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para_plus_bt
CHECKPOINT_DIR=$BACKTRANSLATION/checkpoints/checkpoints_de_ls_para_plus_bt

# --upsample-primary: multiplication factor on how often parallel data is visited
# para has 52805 sents; bt data has around 725000
# factor 14 creates a ratio of around 1:1
fairseq-train $COMBINED \
    --upsample-primary 14 \
    --source-lang de --target-lang ls \
    --arch transformer --share-decoder-input-output-embed \
    --optimizer adam --adam-betas '(0.9, 0.98)' --clip-norm 0.0 \
    --lr 5e-4 --lr-scheduler inverse_sqrt --warmup-updates 4000 \
    --dropout 0.3 --weight-decay 0.0001 \
    --criterion label_smoothed_cross_entropy --label-smoothing 0.1 \
    --max-tokens 4096 \
    --eval-bleu \
    --eval-bleu-args '{"beam": 5, "max_len_a": 1.2, "max_len_b": 10}' \
    --eval-bleu-detok moses \
    --eval-bleu-remove-bpe \
    --eval-bleu-print-samples \
    --best-checkpoint-metric bleu --maximize-best-checkpoint-metric \
    --save-dir $CHECKPOINT_DIR \
    --patience 10

cp $DATA_BIN/simplewiki_de_ls_para/code $CHECKPOINT_DIR/code
cp $DATA_BIN/simplewiki_de_ls_para/dict.de.txt $CHECKPOINT_DIR/dict.de.txt
cp $DATA_BIN/simplewiki_de_ls_para/dict.ls.txt $CHECKPOINT_DIR/dict.ls.txt
