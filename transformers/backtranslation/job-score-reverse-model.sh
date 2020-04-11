#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --qos=vesta
#SBATCH --partition=volta

# calling script needs to set:
# $REPO

REPO=$1

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

DATA_BIN=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para
CHECKPOINT_DIR=$BACKTRANSLATION/checkpoints/checkpoints_ls_de_reverse_model

GENERATION_OUT=$BACKTRANSLATION/generation/reverse_model
REFERENCE=$REPO/data/de_ls/test.de
MOSES=$TRANSFORMERS/software/mosesdecoder

fairseq-generate $DATA_BIN \
    --path $CHECKPOINT_DIR/checkpoint_best.pt \
    --max-tokens 4096 \
    --beam 5 \
> $GENERATION_OUT/test.out

echo "Postprocessing..."
grep -P '^H-' $GENERATION_OUT/test.out \
| sed "s/\@\@ //g" \
| perl $MOSES/scripts/tokenizer/detokenizer.perl -l de -q \
| awk -F'H-' '{print $2}' \
| sort -n \
| cut -f 3 \
> $GENERATION_OUT/test.de.translated

echo "Calculating BLEU..."
cat $GENERATION_OUT/test.de.translated | sacrebleu $REFERENCE
