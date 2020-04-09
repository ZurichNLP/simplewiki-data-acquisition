#!/bin/bash

BACKTRANSLATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
TRANSFORMERS=$(dirname "$BACKTRANSLATION")
REPO=$(dirname "$TRANSFORMERS")

cd $BACKTRANSLATION

TEXT=$BACKTRANSLATION/data-txt/simplewiki_ls_mono
BT_OUT=$BACKTRANSLATION/generation/backtranslations
LOGS=$BACKTRANSLATION/logs/bt_generation

mkdir -p $BT_OUT $LOGS

module load volta cuda/10.0

for CHUNK in $(seq -f "%02g" 0 13); do
    INPUT=$TEXT/train.mono.dedup.${CHUNK}.ls
    OUTPUT=$BT_OUT/bt.chunk${CHUNK}.out

    if [[ -f $OUTPUT ]]; then
        NUM_LINES_INPUT=$(cat $INPUT | wc -l)
        NUM_LINES_OUTPUT=$(awk '/^H-/{hypos++}END{print hypos}' $OUTPUT)
        SKIPPED=$(grep -Po \
            '(?<=WARNING | fairseq.data.data_utils | )\d+(?= samples have invalid sizes and will be skipped)' $OUTPUT)
        if [[ -z "$SKIPPED" ]]; then
            SKIPPED=0
        fi

        if [[ $NUM_LINES_INPUT == $(($NUM_LINES_OUTPUT + $SKIPPED)) ]]; then
            echo "chunk $CHUNK OK: ($NUM_LINES_INPUT input == $NUM_LINES_OUTPUT output + $SKIPPED skipped)."
            continue
        fi
    fi

    # generating back-translation with beam size 5
    sbatch -D $BACKTRANSLATION -o $LOGS/slurm-%j-translate-chunk-$CHUNK.out \
        $BACKTRANSLATION/job-translate-bt-chunk.sh $REPO $CHUNK
done
