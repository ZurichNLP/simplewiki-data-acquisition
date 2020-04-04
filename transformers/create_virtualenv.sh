#!/bin/bash

TRANSFORMERS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO=`dirname "$TRANSFORMERS"`

cd $TRANSFORMERS

module load generic anaconda3
conda create --prefix $TRANSFORMERS/venvs/env-fairseq pip
