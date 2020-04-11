#!/bin/bash
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=generic

# calling script needs to set:
# $REPO

REPO=$1

TRANSFORMERS=$REPO/transformers
BACKTRANSLATION=$TRANSFORMERS/backtranslation

cd $BACKTRANSLATION

BT_OUT=$BACKTRANSLATION/generation/backtranslations
BT_TXT=$BACKTRANSLATION/data-txt/simplewiki_ls_bt
BT_BIN=$BACKTRANSLATION/data-bin/simplewiki_ls_bt
SRC_DICT=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para/dict.de.txt
PARA_BIN=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para
COMBINED=$BACKTRANSLATION/data-bin/simplewiki_de_ls_para_plus_bt

echo "Extracting back-translations from out files..."
python $TRANSFORMERS/software/fairseq/examples/backtranslation/extract_bt_data.py \
    --minlen 1 --maxlen 250 --ratio 1.5 \
    --output $BT_TXT/bt_data_full --srclang de --tgtlang ls \
    $BT_OUT/bt.chunk*.out

paste $BT_TXT/bt_data_full.de $BT_TXT/bt_data_full.ls \
| shuf \
| awk -F '\t' -v BT_TXT="$BT_TXT" \
    '{if (NR <= 52805) print $1 > BT_TXT"/bt_data.de"; if (NR <= 52805) print $2 > BT_TXT"/bt_data.ls";}'

echo "Binarizing back-translation data..."
fairseq-preprocess \
    --source-lang de --target-lang ls \
    --joined-dictionary \
    --srcdict $SRC_DICT \
    --trainpref $BT_TXT/bt_data \
    --destdir $BT_BIN \
    --workers 8

echo "Creating a combined dataset in $COMBINED..."
PARA_BIN=$(readlink -f $PARA_BIN)
BT_BIN=$(readlink -f $BT_BIN)

for LANG in de ls; do \
    ln -s $PARA_BIN/dict.$LANG.txt $COMBINED/dict.$LANG.txt; \
    for EXT in bin idx; do \
        ln -s $PARA_BIN/train.de-ls.$LANG.$EXT $COMBINED/train.de-ls.$LANG.$EXT; \
        ln -s $BT_BIN/train.de-ls.$LANG.$EXT $COMBINED/train1.de-ls.$LANG.$EXT; \
        ln -s $PARA_BIN/valid.de-ls.$LANG.$EXT $COMBINED/valid.de-ls.$LANG.$EXT; \
        ln -s $PARA_BIN/test.de-ls.$LANG.$EXT $COMBINED/test.de-ls.$LANG.$EXT; \
    done; \
done

ln -s $PARA_BIN/code $COMBINED/code
