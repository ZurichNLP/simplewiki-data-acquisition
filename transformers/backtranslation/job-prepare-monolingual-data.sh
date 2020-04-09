#!/bin/bash
#SBATCH --time=00:30:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=generic

# calling script needs to set:
# $REPO

REPO=$1

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

MOSES=$TRANSFORMERS/software/mosesdecoder
SUBWORD_NMT=$TRANSFORMERS/software/subword-nmt

DATA=$REPO/data
OUT_TXT=$BACKTRANSLATION/data-txt/simplewiki_ls_mono
OUT_BIN=$BACKTRANSLATION/data-bin/simplewiki_ls_mono

CODE=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para/code
SRC_DICT=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para/dict.ls.txt
TGT_DICT=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para/dict.de.txt
CHUNK_SIZE=100000

echo "Preprocessing data..."
cat $DATA/simple_ls/train.ls \
| perl $MOSES/scripts/tokenizer/normalize-punctuation.perl -l de \
| perl $MOSES/scripts/tokenizer/remove-non-printing-char.perl \
| perl $MOSES/scripts/tokenizer/tokenizer.perl -threads 8 -a -l de \
> $DATA/simple_ls/tmp/train.tok.ls

echo "Applying BPE on $DATA/simple_ls/tmp/train.tok.ls..."
python $SUBWORD_NMT/subword_nmt/apply_bpe.py -c $CODE \
    < $DATA/simple_ls/tmp/train.tok.ls \
    > $DATA/simple_ls/tmp/train.bpe.ls

echo "Deduplicating $DATA/simple_ls/tmp/train.bpe.ls..."
python $TRANSFORMERS/software/fairseq/examples/backtranslation/deduplicate_lines.py \
    < $DATA/simple_ls/tmp/train.bpe.ls \
    > $DATA/simple_ls/tmp/train.dedup.ls

echo "Splitting into chunks of size $CHUNK_SIZE"
split --lines $CHUNK_SIZE --numeric-suffixes -a 2 \
    --additional-suffix .ls \
    $DATA/simple_ls/tmp/train.dedup.ls \
    $OUT_TXT/train.mono.dedup.

for CHUNK in $(seq -f "%02g" 0 13); do
    fairseq-preprocess \
        --only-source \
        --source-lang ls --target-lang de \
        --joined-dictionary \
        --srcdict $SRC_DICT \
        --testpref $OUT_TXT/train.mono.dedup.${CHUNK} \
        --destdir $OUT_BIN/chunk${CHUNK} \
        --workers 8; \
    cp $TGT_DICT $OUT_BIN/chunk${CHUNK}/; \
    cp $CODE $OUT_BIN/chunk${CHUNK}/; \
done
