# simplewiki_project

This repository contains scripts that were created by Nicolas Spring during a programming project at the [University of Zurich](https://www.uzh.ch/en.html).

The scripts in this repository were created in the context of working with data from the [Simple English Wikipedia](https://simple.wikipedia.org/wiki/Main_Page), but they can easily be adapted for other languages and use cases. They are structured into four main parts:

- **parsing:** Creating a dataset from files in [Medialab Document Format](http://medialab.di.unipi.it/wiki/Document_Format).
- **translation:** Translating sentences of the dataset with the API of your choice. For this part, the [DeepL API V2](https://www.deepl.com/docs-api/accessing-the-api/api-versions) was used.
- **alignment:** Finding sentences in the Simple English Wikipedia that occurred in the same form in the [Simple English Wikipedia Dataset](http://ssli.ee.washington.edu/tial/projects/simplification/).
- **transformers**: Training translation models on the data.

Further information and examples can be found in the respective subdirectories.

The "misc" directory contains small utility scripts for various tasks.

### Requirements:

- Python 3.6
- The packages listed in the `requirements.txt` file.
- For the "transformers" part, a virtual environment is created. Scripts to install the required software are provided.

