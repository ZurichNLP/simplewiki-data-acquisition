#!/bin/bash

TRANSFORMERS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO=`dirname "$TRANSFORMERS"`

cd $TRANSFORMERS

conda install pytorch torchvision cudatoolkit=10.0 -c pytorch

pip install Cython sacremoses subword_nmt sacrebleu==1.4.4

mkdir -p $TRANSFORMERS/software
git clone https://github.com/pytorch/fairseq $TRANSFORMERS/software/fairseq
cd $TRANSFORMERS/software/fairseq
pip install .
