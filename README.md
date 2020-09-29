# **simplewiki-data-acquisition**

This repository is a collection of data acquisition scripts used to create a parallel corpus of genuine German and synthetic simplified German data.

The scripts in this repository were created in the context of primarily working with data from the [Simple English Wikipedia](https://simple.wikipedia.org/wiki/Main_Page), but they can easily be adapted for other languages and use cases. They are structured into five main parts:

- **parsing:** Creating a dataset from files in [Medialab Document Format](http://medialab.di.unipi.it/wiki/Document_Format).
- **translation:** Translating sentences of the dataset with the API of your choice. For this part, the [DeepL API V2](https://www.deepl.com/docs-api/accessing-the-api/api-versions) was used.
- **alignment:** Finding sentences in the Simple English Wikipedia that occurred in the same form in the [Simple English Wikipedia Dataset](http://ssli.ee.washington.edu/tial/projects/simplification/).
- **transformers**: Training toy translation models on the data.
- **misc:** Small utility scripts for various tasks.

Further information and examples can be found in the respective subdirectories.

### Requirements:

- Python 3.6
- The packages listed in the `requirements.txt` file.
- For the "transformers" part, a virtual environment is created. Scripts to install the required software are provided.

