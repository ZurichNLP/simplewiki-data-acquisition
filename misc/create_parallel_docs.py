import argparse
import csv
import os
import re
import sys
from typing import Dict, IO, Tuple

import pandas as pd


def parse_args(): # python3 create_parallel_docs.py --simple-tsv simplede_all.tsv --de-tsv de.tsv --out-dir my_out
    parser = argparse.ArgumentParser()
    parser.add_argument('--simple-tsv', type=argparse.FileType('r'), metavar='PATH',
                        help='tsv containing simple sentences and information on article pairs')
    parser.add_argument('--de-tsv', type=argparse.FileType('r'), metavar='PATH',
                        help='tsv containing the standard german articles')
    parser.add_argument('--out-dir', type=str, metavar='PATH',
                        help='output directory for article pairs')
    args = parser.parse_args()
    return args


def map_tsv(tsv_file: IO) -> Dict[int, Tuple[int, int]]:
    """
    creates a dict mapping article ids to the position in the file where the article starts
    and the number of lines the article contains.
    """
    sys.stderr.write("Mapping articles to lines in the de tsv file...\n")
    last_id = None
    document_start = 0
    current_line = 0
    mapping_dict = dict()
    article_length = 0
    mapped_articles = 0

    line = tsv_file.readline()
    while line:
        article_id = int(line.split('\t')[0])
        # new article begins
        if article_id != last_id:
            if last_id == None:
                mapping_dict[article_id] = (document_start, article_length)
            else:
                mapping_dict[last_id] = (document_start, article_length)
            document_start = current_line
            article_length = 0
            last_id = article_id
            mapped_articles += 1

            if mapped_articles % 100000 == 0:
                sys.stderr.write(f"Mapped {mapped_articles} de articles...\n")

        article_length += 1
        current_line = tsv_file.tell()
        line = tsv_file.readline()

    mapping_dict[last_id] = (document_start, article_length)

    sys.stderr.write(f"Done, mapped {len(mapping_dict)} articles to lines.\n")
    return mapping_dict


def write_de_article(start: int, n_lines: int, tsv_file: IO, output_path: str):
    """
    writes the de article to the specified file.
    """
    tsv_file.seek(start)    
    de_fieldnames = ["de_article_id",
                     "de_section_id",
                     "de_sent_id",
                     "de_url",
                     "de_article_title",
                     "de_section_title",
                     "de_sent"]
    de_reader = csv.DictReader(tsv_file, de_fieldnames, delimiter='\t')
    with open(output_path, 'w') as outfile:
        for _ in range(n_lines):
            line = next(de_reader)
            outfile.write(line["de_sent"] + '\n')


def create_doc_pairs(simple_tsv: IO,
                     de_tsv: IO,
                     lookup_dict: Dict[int, Tuple[int, int]],
                     output_dir: str):
    """
    creates parallel document pairs with unique indices
    """
    sys.stderr.write("Creating output documents...\n")
    id_regex = re.compile(r".*wiki\?curid=(\d+)")

    last_line = None
    last_article_lines = []
    simple_fieldnames = ["simple_article_id",
                         "simple_section_id",
                         "simple_sent_id",
                         "simple_url",
                         "simple_article_title",
                         "simple_section_title",
                         "simple_sent",
                         "de_article_title",
                         "de_url",
                         "simplede_sent"]
    completed = 0
    simple_reader = csv.DictReader(simple_tsv, simple_fieldnames, delimiter='\t')
    for line in simple_reader:
        # no exact match (see https://github.com/nicolasspring/simplewiki_project/blob/master/parsing/README.md#output)
        if line["de_url"] == "NOT_FOUND":
            continue
        # end of an article
        if (last_line is not None
            and line["simple_article_id"] != last_line["simple_article_id"]):
            de_article_id = id_regex.findall(last_line["de_url"])[0]
            output_prefix = os.path.join(
                                output_dir,
                                last_line["simple_article_id"] + "_" + de_article_id)
            with open(output_prefix + '.simplede', 'w') as outfile:
                for last_line in last_article_lines:
                    outfile.write(last_line + '\n')
            write_de_article(lookup_dict[int(de_article_id)][0],
                             lookup_dict[int(de_article_id)][1],
                             de_tsv,
                             output_prefix + '.de')

            completed += 1
            if completed % 100000 == 0:
                sys.stderr.write(f"Completed {completed} simplede articles...\n")

        last_article_lines.append(line["simplede_sent"])
        last_line = line


    de_article_id = id_regex.findall(last_line["de_url"])[0]
    output_prefix = os.path.join(
                        output_dir,
                        last_line["simple_article_id"] + "-" + de_article_id)
    with open(output_prefix + '.simplede', 'w') as outfile:
        for line in last_article_lines:
            outfile.write(line)
    write_de_article(lookup_dict[int(de_article_id)][0],
                     lookup_dict[int(de_article_id)][1],
                     de_tsv,
                     output_prefix + '.de')

    sys.stderr.write(f"Done, created {completed} output documents.\n")



def main(args: argparse.Namespace):
    de_lines = map_tsv(args.de_tsv)
    create_doc_pairs(args.simple_tsv, args.de_tsv, de_lines, os.path.abspath(args.out_dir))


if __name__ == '__main__':
    args = parse_args()
    main(args)
