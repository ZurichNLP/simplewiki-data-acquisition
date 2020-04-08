# Training Transformer Models for Translation

Scripts in this section train translation models for translation into simplified German (Leichte Sprache; `ls` was used as the ending for files.).



## Remarks

- These scripts use [conda](https://docs.conda.io/en/latest/) to create a virtual environment. Scripts for creating the environment and installing the required packages are provided.
- [slurm](https://slurm.schedmd.com/documentation.html) is used to submit jobs.
- Model training is done with [fairseq](https://github.com/pytorch/fairseq).



## Virtual Environment

To create a virtual environment, please use the following command.

```bash
bash create_virtualenv.sh
```

Please activate the environment. All further steps assume the environment is active. To install the necessary software:

```bash
bash install_packages.sh
```



## Training a Transformer Base Model

### Data

The path to the data in these scripts is `simplewiki_project/data/de_ls/`. This directory contains six files: `{train,test,valid}.{de,ls}`.

### Preprocessing

To preprocess the data, please use the following command:

```bash
bash base_transformer/prepare_de_ls_data.sh
```

This step normalizes and tokenizes the data, applies BPE and uses fairseq to binarize the data.

### Training

Training a transformer base model:

```bash
bash base_transformer/train_base_transformer.sh
```

This trains a transformer translation model on the preprocessed data. The training has an early stopping patience of 10 and uses the BLEU score on the validation set as the metric.

### Scoring

Scoring the model:

```bash
bash base_transformer/score_base_transformer.sh
```

The BLEU score is calculated on the postprocessed and detokenized test set.