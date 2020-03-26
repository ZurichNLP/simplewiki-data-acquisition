# Finding Unchanged Sentences and Aligning them to English Counterparts

### Parallel Wikipedia Dataset

The script in this section was used to compare sentences extracted from the present-day Simple English Wikipedia to the sentences in the [Parallel Wikipedia Dataset](http://ssli.ee.washington.edu/tial/projects/simplification/) extracted by [Hwang et al. (2015)](https://www.aclweb.org/anthology/N15-1022/). It extracts exact counterparts (casing and punctuation can be ignored).



### Input

The input for this script are parsed TSV files in the form of the output of the `../parsing/parse_documents.py` script:

| article id | section id | sent id | article URL                                                  | article title | section title | sent                                            |
| ---------- | ---------- | ------- | ------------------------------------------------------------ | ------------- | ------------- | ----------------------------------------------- |
| 178        | 1          | 1       | [https://simple.wikipedia.org/wiki?curid=178](https://simple.wikipedia.org/wiki?curid=178) | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea. |

Of course, other files can be processed as well, but this may need some slight tweaks on the script.



### Output

In the output, the information from the Parallel Wikipedia Dataset and the document parsing step are combined into a single file containing seven columns:

| alignment file name           | alignment sent simple                            | alignment sent english                                       | article id | section id | sent id | parsed sent                                     |
| ----------------------------- | ------------------------------------------------ | ------------------------------------------------------------ | ---------- | ---------- | ------- | ----------------------------------------------- |
| aligned-good_partial-0.53.txt | Cuba is an island country in the Caribbean Sea . | Cuba , officially the Republic of Cuba ( i \/ ˈkjuːbə \/ ; Spanish : República de Cuba , pronounced : ( reˈpuβlika ðe ˈkuβa ) ( listen ) ) , is an island country in the Caribbean . | 178        | 1          | 1       | Cuba is an island country in the Caribbean Sea. |

The information in the first three columns is taken from the Parallel Wikipedia Dataset and allows for identifying the sentence in the file(s). The other four columns are taken from the parsed TSV file(s) and allow for identifying the sentence in the parsed TSV file(s).



### Examples

Information on the arguments of `find_unchanged.py`:

```bash
python find_unchanged.py -h
```

To extract unchanged sentences from the Parallel Wikipedia Dataset and create a TSV file with the sentences in Simple English and English:

```bash
ALIGNMENT_FILES=(
    "/path/to/alignment_file_1.txt"
    "/path/to/alignment_file_2.txt"
)
PARSED_FILES=(
    "/path/to/parsed_file_1.tsv"
    "/path/to/parsed_file_2.tsv"
)
OUTPUT=/path/to/output_file.tsv

python alignments.py -a "${ALIGNMENT_FILES[@]}" -p "${PARSED_FILES[@]}" -o $OUTPUT -c 6
```

