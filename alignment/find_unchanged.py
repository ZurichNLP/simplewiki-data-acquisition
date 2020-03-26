#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import argparse
import pandas as pd
import re

from string import punctuation
from typing import List, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--alignment-file', nargs='+', type=str, metavar='PATH',
                        help='One or more tsv files containing simplewiki corpus alignments.')
    parser.add_argument('-c', '--column-index', type=int, metavar='INT', default=6,
                        help='An integer (starting at 0) signifying the index of the column ' + \
                        'containing Simple English sentences.')
    parser.add_argument('-o', '--output', type=str, metavar='PATH',
                        help='The output path for the file with corresponding sentences.')
    parser.add_argument('-p', '--parsed-file', nargs='+', type=str, metavar='PATH',
                        help='One or more tsv files containing parsed wikipedia articles.')
    args = parser.parse_args()
    return args


def read_alignment_file(path: str) -> pd.DataFrame:
    '''
    reads an tsv alignment file into a pd.DataFrame.

    Args:
        path:   the path to a tsv file containing en-simple wikipedia alignments.
    '''
    filename = path.split('/')[-1] if '/' in path else path
    df = pd.read_csv(path, delimiter='\t', names=['en', 'simple', 'score'])
    df.insert(3, 'filename', pd.Series([filename for n in range(len(df))]))
    return df

def read_parsed_wiki(path: str, column_index: int = 6) -> pd.DataFrame:
    '''
    reads a tsv file and returns all columns up to and including the specified one.

    Args:
        path:   the path to a tsv file containing the parsing output.
    '''
    df = pd.read_csv(path, sep='\t', header=None, quotechar='"').loc[:, :column_index]
    return df

def find_pendants(simple_dfs: List[pd.DataFrame], alignment_dfs: List[pd.DataFrame], fuzzy: bool = False) -> pd.DataFrame:
    '''
    finds lines in both the simplewiki dfs and the alignment dfs and returns a pd.DataFrame.

    Args:
        simple_dfs:     a list of pd.DataFrames read from parsed tsv files.
        alignment_dfs:  a list of pd.DataFrames read from the alignment files.

    Returns:
        df:             a pd.DataFrame containing the following columns:
                            alignment_file_name,
                            alignment_sent_simple,
                            alignment_sent_en,
                            article_id,
                            section_id,
                            sent_id,
                            parsed_sent
    '''
    simple_df = merge_dfs(simple_dfs)
    alignment_df = merge_dfs(alignment_dfs)
    sent_lookup = make_sent_lookup_dict(alignment_df, 'simple', fuzzy)

    df_dict = {}
    for i, row in simple_df.iterrows():
        sent = remove_punctuation_and_lowercase(row[6]).strip() if fuzzy else row[6]
        if sent == '': # sents containing nothing apart from whitespace and punctuation
            continue
        found = sent_lookup.get(sent, None)
        if found != None and found['simple'].strip() != '': # sents containing nothing apart from whitespace and punctuation
            df_dict[i] = (found['filename'], found['simple'], found['en'], row[0], row[1], row[2], row[6])

    output_cols = ['alignment_file_name',
                   'alignment_sent_simple',
                   'alignment_sent_en',
                   'article_id',
                   'section_id',
                   'sent_id',
                   'parsed_sent']
    df = pd.DataFrame.from_dict(df_dict, orient='index', columns=output_cols)
    return df
        

def merge_dfs(df_list: List[pd.DataFrame]) -> pd.DataFrame:
    '''
    concatenates a list of pd.DataFrames with the same number of columns into one.

    Args:
        df_list:    a list of pd.DataFrames with the same number of columns

    Returns:
        concat:     a pd.DataFrame with as many entries as all the pd.DataFrames in *df_list* combined.
    '''
    concat = df_list[0]
    if len(df_list) > 1:
        for df in df_list[1:]:
            concat = concat.append(df, ignore_index=True)
    return concat

def make_sent_lookup_dict(df: pd.DataFrame, col_name: str, fuzzy: bool = False) -> Dict[str, Dict[str, str]]:
    '''
    takes a pd.DataFrame and converts it into a dict with sents as keys.

    Args:
        df:         a pd.DataFrame.
        col_name:   the name of the column containing the sents to be used as keys.
        fuzzy:      a boolean specifying whether or not so simplify the sentence keys.

    Returns:
        sent_dict:  a dict containing sentences as keys and a dict of column values as values.
    '''
    df_dict = df.to_dict('index')
    sent_dict = {}
    for i, row in df_dict.items():
        if fuzzy:
            sent_dict[remove_punctuation_and_lowercase(row[col_name]).strip()] = row
        else:
            sent_dict[col_name.strip()] = row
    return sent_dict

def remove_punctuation_and_lowercase(input_string: str) -> str:
    '''
    removes punctuation lowercases a string.

    Args:
        input_string:   a str

    Returns:
        ret_str:        the lowercased input string with removed punctuation.
    '''
    ret_str = re.sub(r'\s+', r' ', input_string.translate(str.maketrans('', '', punctuation)))
    return ret_str


def main(args: argparse.Namespace):
    parsed_files = [read_parsed_wiki(path, args.column_index) for path in args.parsed_file]
    alignment_files = [read_alignment_file(path) for path in args.alignment_file]

    ret_df = find_pendants(parsed_files, alignment_files, fuzzy=True)
    ret_df.to_csv(args.output, sep='\t', quotechar='"', index=False, header=False)


if __name__ == '__main__':
    args = parse_args()
    main(args)
