# Translating Sentences

### Input

The script `translate_sents.py` accepts a TSV file as the input. This can be the output from document parsing, but this does not need to be the case. The index of the column can be specified (the default index is 6).

An input file may look like this:

| article id | section id | sent id | article URL                                                  | article title | section title | sent                                            |
| ---------- | ---------- | ------- | ------------------------------------------------------------ | ------------- | ------------- | ----------------------------------------------- |
| 178        | 1          | 1       | [https://simple.wikipedia.org/wiki?curid=178](https://simple.wikipedia.org/wiki?curid=178) | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea. |



### Output

The output file contains an additional column with the translated sentence:

| ...  | sent id | article URL                                                  | article title | section title | sent                                            | translation                             |
| ---- | ------- | ------------------------------------------------------------ | ------------- | ------------- | ----------------------------------------------- | --------------------------------------- |
| ...  | 1       | [https://simple.wikipedia.org/wiki?curid=178](https://simple.wikipedia.org/wiki?curid=178) | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea. | Kuba ist ein Inselstaat in der Karibik. |

The translation column will never be inserted between existing columns and thus will always be added as the last column of the new file.

There exists the possibility to specify an additional output file (`--save-file`) to which translations are saved as soon as they are obtained. This file can act as a backup when working with big chunks or when working with an unreliable connection.

The save file contains one sentence per line with no additional information:

```
Kuba ist ein Inselstaat in der Karibik.
Das Land besteht aus der großen Insel Kuba, der Insel Isla de la Juventud ("Insel der Jugend") und vielen kleineren Inseln.
...
```



### API

The scripts in this directory use the class `DeeplConnector` to translate sentences using the [DeepL API V2](https://www.deepl.com/docs-api/accessing-the-api/api-versions). In this form, the arguments and structure of the scripts is specific for this API. There are arguments for the authorization key and the source and target languages.

The easiest way to use a different API is to pass a custom class instance to the `translate_column` method of the `TranslationHandler` class. If your class implements a `translate_sentences(sents: List[str], source_lang: str, target_lang: str) -> List[str]:` method, this will work without any additional tweaks.



### Examples

Information on the arguments of `translate_sents.py`:

```bash
python translate_sents.py -h
```

Translating the sentences in a dataset:

```bash
INPUT=/path/to/input_file.tsv
COLUMN_INDEX=6 # the index (starting with 0) of the column containing the sentences
SAVE_FILE=/path/to/save_file.txt
OUTPUT=/path/to/output_file.tsv

python translate_sents.py -i $INPUT --save-file $SAVE_FILE -o $OUTPUT \
        --auth-key "your-api-key" --source-lang EN --target-lang DE \
        -c $COLUMN_INDEX -v 11
```


