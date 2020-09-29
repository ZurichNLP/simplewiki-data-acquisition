# Training Transformer Models for Translation

Scripts in this section train toy models for translation into simplified German (`ls` was used as the ending for files.).



## Remarks

- The scripts use [conda](https://docs.conda.io/en/latest/) to create a virtual environment. Scripts for creating the environment and installing the required packages are provided.
- [slurm](https://slurm.schedmd.com/documentation.html) is used to submit jobs.
- Model training is done with [fairseq](https://github.com/pytorch/fairseq).



## Virtual Environment

To create a virtual environment, please use the following command.

```bash
bash create_virtualenv.sh
```

Please activate the environment. **All further steps assume the environment is active.** 

To install the necessary software:

```bash
bash install_packages.sh
```



## Training a Baseline Transformer Model

### Data

The default path to the data in these scripts is `simplewiki_project/data/de_ls/`. This directory contains six files: `{train,test,valid}.{de,ls}`. Please change the paths accordingly.

### Preprocessing

To preprocess the data, please use the following command:

```bash
bash base_transformer/prepare_de_ls_data.sh
```

This step normalizes and tokenizes the data, applies BPE and uses `fairseq` to binarize the data.

### Training

Training a transformer baseline model:

```bash
bash base_transformer/train_base_transformer.sh
```

This trains a transformer translation model on the preprocessed data. The training has an early stopping patience of 10 and uses the BLEU score on the validation set to decide when to stop training.

### Scoring

Scoring the model:

```bash
bash base_transformer/score_base_transformer.sh
```

The BLEU score is calculated on the postprocessed and detokenized test set.



## Training a Transformer Model with Back-Translation

### Data

The path to the parallel data is `simplewiki_project/data/de_ls/`. This directory contains six files: `{train,test,valid}.{de,ls}`. The file `simplewiki_project/data/simple_ls/train.ls` contains the monolingual target data. Please change the paths accordingly.

### Preprocessing

To preprocess the data, please use the following command:

```bash
bash backtranslation/prepare_data.sh
```

This prepares the parallel data in the exact same way as for the baseline model. Additionally, the monolingual data is tokenized, BPE is applied and duplicate lines are removed. It is being split in chunks of size 100'000 which are binarized individually.

### Training a Reverse Model for Back-Translation

Training a reverse model to translate simplified German to German:

```bash
bash backtranslation/train_reverse_model.sh
```

This trains a transformer translation model on the parallel data. The training has an early stopping patience of 10 and uses the BLEU score on the validation set to decide when to stop training.

Evaluate the model to make sure it is well trained:

```bash
bash backtranslation/score_reverse_model.sh
```

### Generating Back-Translations

Translating the monolingual chunks:

```bash
bash backtranslation/generate_bt.sh
```

Please rerun the script after translation has completed to verify the number of translations that were produced.

Extracting the back-translations, applying length and ration filters and symlinking with the parallel data to create a combined dataset `simplewiki_project/transformers/backtranslation/data-bin/simplewiki_de_ls_para_plus_bt`:

```bash
bash backtranslation/create_combined_dataset.sh
```

The combined dataset contains parallel and back-translated data in a 1:1 ratio.

### Training a Model on the Combined Data

Training a model on the combined data:

```bash
bash backtranslation/train_bt_model.sh
```

### Scoring

Scoring the model:

```bash
bash backtranslation/score_bt_model.sh
```

The BLEU score is calculated on the postprocessed and detokenized test set.