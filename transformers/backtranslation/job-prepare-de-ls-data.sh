#!/bin/bash
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=8G
#SBATCH --partition=generic

# calling script needs to set:
# $REPO

REPO=$1

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

SRC=de
TGT=ls
PAIR=$SRC-$TGT

MOSES=$TRANSFORMERS/software/mosesdecoder
SUBWORD_NMT=$TRANSFORMERS/software/subword-nmt

DATA=$REPO/data
OUT_TXT=$BACKTRANSLATION/data-txt/simplewiki_de_ls_para
OUT_BIN=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para

echo "Preprocessing data..."
for l in $SRC $TGT; do
    for c in train test valid; do
        cat $DATA/de_ls/$c.$l \
        | perl $MOSES/scripts/tokenizer/normalize-punctuation.perl -l de \
        | perl $MOSES/scripts/tokenizer/remove-non-printing-char.perl \
        | perl $MOSES/scripts/tokenizer/tokenizer.perl -threads 8 -a -l de \
        > $DATA/de_ls/tmp/$c.tok.$l
    done
done

CODE=$OUT_TXT/code
CONCAT=$DATA/de_ls/tmp/train.$PAIR
rm -f $CONCAT
for l in $SRC $TGT; do
    cat $DATA/de_ls/tmp/train.tok.$l >> $CONCAT
done

echo "Learning BPE on $CONCAT..."
python $SUBWORD_NMT/subword_nmt/learn_bpe.py -s 10000 < $CONCAT > $CODE

for l in $SRC $TGT; do
    for c in train test valid; do
        INFILE=$DATA/de_ls/tmp/$c.tok.$l
        echo "Applying BPE to $INFILE..."
        python $SUBWORD_NMT/subword_nmt/apply_bpe.py -c $CODE \
            < $INFILE \
            > $DATA/de_ls/tmp/$c.bpe.$l
    done
done

echo "Cleaning training corpus..."
perl $MOSES/scripts/training/clean-corpus-n.perl -ratio 1.5 $DATA/de_ls/tmp/train.bpe $SRC $TGT $OUT_TXT/train 1 250

cp $DATA/de_ls/tmp/test.bpe.$SRC $OUT_TXT/test.$SRC
cp $DATA/de_ls/tmp/test.bpe.$TGT $OUT_TXT/test.$TGT
cp $DATA/de_ls/tmp/valid.bpe.$SRC $OUT_TXT/valid.$SRC
cp $DATA/de_ls/tmp/valid.bpe.$TGT $OUT_TXT/valid.$TGT

rm -f $OUT_BIN/simplewiki_de_ls/dict.de.txt $OUT_BIN/simplewiki_de_ls/dict.ls.txt

fairseq-preprocess \
    --joined-dictionary \
    --source-lang de --target-lang ls \
    --trainpref $OUT_TXT/train --testpref $OUT_TXT/test --validpref $OUT_TXT/valid \
    --destdir $OUT_BIN --thresholdtgt 0 --thresholdsrc 0 \
    --workers 8

cp $CODE $OUT_BIN/code
