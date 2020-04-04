#!/bin/bash

TRANSFORMERS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO=`dirname "$TRANSFORMERS"`

cd $TRANSFORMERS

conda install pytorch torchvision cudatoolkit=10.0 -c pytorch

pip install Cython

pip install fairseq
