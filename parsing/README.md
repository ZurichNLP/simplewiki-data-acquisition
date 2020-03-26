# Creating a Dataset from (Wikipedia) Articles

### Input

The input for the scripts in this directory are files in [Medialab Document Format](http://medialab.di.unipi.it/wiki/Document_Format). When working with Wikipedia dumps, an easy way to obtain such files is using the [WikiExtractor](https://github.com/attardi/wikiextractor).

Example of an input file:

```
</doc>
<doc id="402315" url="https://simple.wikipedia.org/wiki?curid=402315" title="Huron, South Dakota">
Huron, South Dakota

Huron is a city in the eastern part of South Dakota, United States. It is the county seat of Beadle County, and 12,592 people lived there at the 2010 census. Huron became a city in 1883.



</doc>
<doc id="402318" url="https://simple.wikipedia.org/wiki?curid=402318" title="Nomascus">
Nomascus

Nomascus is the second most common genus (biology) of Gibbon. There are six species in the genus. Originally Nomascus was a sub-genus of the Hylobatidae.


</doc>
```

Raw Wikipedia dumps can be downloaded from [https://dumps.wikimedia.org/](https://dumps.wikimedia.org/).



### Output

The script `parse_documents.py` creates TSV files as output. In the base form, they have seven columns:

| article id | section id | sent id | article URL                                                  | article title | section title | sent                                            |
| ---------- | ---------- | ------- | ------------------------------------------------------------ | ------------- | ------------- | ----------------------------------------------- |
| 178        | 1          | 1       | [https://simple.wikipedia.org/wiki?curid=178](https://simple.wikipedia.org/wiki?curid=178) | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea. |

However, additional columns may be added. When checking if articles exist in a different language, a column with the article title in the other language will be added. When looking up articles in German, the output file may look like this:

| ...  | article URL                                                  | article title | section title | sentence                                        | foreign title |
| ---- | ------------------------------------------------------------ | ------------- | ------------- | ----------------------------------------------- | ------------- |
| ...  | [https://simple.wikipedia.org/wiki?curid=178](https://simple.wikipedia.org/wiki?curid=178) | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea. | Kuba          |

When also extracting the URLs of the foreign articles, the output file may look like this:

| ...  | article title | section title | sentence                                                     | foreign title | foreign URL                                                  |
| ---- | ------------- | ------------- | ------------------------------------------------------------ | ------------- | ------------------------------------------------------------ |
| ...  | Cuba          | Summary       | Cuba is an island country in the Caribbean Sea.              | Kuba          | [https://de.wikipedia.org/wiki?curid=7842](https://de.wikipedia.org/wiki?curid=7842) |
| ...  | Goatee        | Summary       | A goatee is a beard formed by a tuft of hair under the chin, resembling that of a billy goat. | Goatee        | NOT_FOUND                                                    |

**Note**: It is possible that URL extraction fails for some articles. This occurs when articles are not perfectly equivalent but they are still linked in the langlinks table. This can happen in two cases: First when a "full" article links to a subsection of an article in an other language. An example of this is the Simple English article [Goatee](https://simple.wikipedia.org/wiki/Goatee) being linked to the German article [Barthaar#Bartformen](https://de.wikipedia.org/wiki/Barthaar#Bartformen). The second case is a linked title that does not contain their own article. An example of this is the Simple English article [Apple](https://simple.wikipedia.org/wiki/Apple) being linked to the German title [Tafelapfel](https://de.wikipedia.org/w/index.php?title=Tafelapfel&redirect=no), which is automatically redirected to the article [Kulturapfel](https://de.wikipedia.org/wiki/Kulturapfel) (both examples were last checked on 26.03.2020). In both cases, the `parse_documents.py` script will add a `NOT_FOUND` placeholder string to the foreign URL column.



### The langlinks Table

The langlinks table stores interlanguage links. These are the links to the article in other languages that are typically displayed on the left margin when displaying an article in the browser. It allows for fast lookup and can store one link per language per article (e.g. an article in English cannot be linked to multiple articles in German). Additional information on the langlinks table can be found in the [manual](https://www.mediawiki.org/wiki/Manual:Langlinks_table) and the table can be downloaded from [https://dumps.wikimedia.org/](https://dumps.wikimedia.org/).

The `parse_documents.py` script makes use of the langlinks table to check if an article exists in another language and to extract its title. It assumes that the langlinks table was imported to [MySQL](https://www.mysql.com/de/) database and accesses it using the [MySQL Connector](https://dev.mysql.com/doc/connector-python/en/).



### Examples

Information on the arguments of `parse_documents.py`:

```bash
python parse_documents.py -h
```

Full functionality (reading docs, checking if the article exists in another language, looking up URLs of articles in the other language Wikipedia):

```bash
DOCS=/path/to/docs/
MATCHES=/path/to/match_out_file.tsv
NOMATCH=/path/to/no_match_out_file.tsv
OTHER_LANG_DOCS=/path/to/docs/
URL_OUT=/path/to/url_out_file.tsv

# please adjust user, host and database to access the langlinks table
# in your mysql database.

python parse_documents.py -i $DOCS --input-urls $OTHER_LANG_DOCS \
        --match $MATCHES --no-match $NOMATCH --output-url-file $URL_OUT \
        --db-user username --db-host host --db-database database \
         -p 8 -f 5 -v 1 --input-lang EN --match-lang de
```

Simple article parsing:

```bash
DOCS=/path/to/docs/
PARSED=/path/to/parsed_out_file.tsv

# param --match provides the single output file when match --match-lang is omitted.
# adding --no-urls deactivates URL lookup.

python parse_documents.py -i $DOCS --match $PARSED \
        -p 8 -f 5 -v 1 --input-lang EN --no-urls
```