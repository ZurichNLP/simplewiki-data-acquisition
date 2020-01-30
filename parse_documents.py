#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring


import argparse
import pathos.multiprocessing as mp
import spacy

from DocumentParser import DocumentParser
from URLFinder import URLFinder


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', type=int,
                        help='The number of files handled per process before writing to the output file.',
                        default=1, metavar='INT')
    parser.add_argument('-i', '--input', type=str,
                        help='A directory containing files in medialab document format for parsing.',
                        metavar='PATH', required=True)
    parser.add_argument('-m', '--match', type=str,
                        help='Output file for articles with a match. ' + \
                        'If no --match-lang is provided, all output will be written to this file.',
                        metavar='PATH')
    parser.add_argument('-n', '--no-match', type=str,
                        help='Output file for articles with no match.',
                        metavar='PATH', default=None)
    parser.add_argument('-p', '--processes', type=int,
                        help='The number of processes to be run in parallel.',
                        default=mp.cpu_count(), metavar='INT')
    parser.add_argument('-v' ,'--verbose', type=int, metavar='INT',
                        help='The verbosity level of the DocumentParser.', default=1)
    parser.add_argument('--db-user', type=str, metavar='STRING',
                        help='The mysql databank user with access to the langlinks table.')
    parser.add_argument('--db-host', type=str, metavar='STRING',
                        help='The host of the databank containing the langlinks table.')
    parser.add_argument('--db-database', type=str, metavar='STRING',
                        help='The mysql database containing the langlinks table.')
    parser.add_argument('--input-lang', type=str, metavar='STRING',
                        help='The language of the input files (EN/DE)',
                        choices=['DE', 'EN'], default='EN')
    parser.add_argument('--input-urls', type=str, metavar='STRING',
                        help='A directory containing files in medialab document format for extracting other language URLs.')
    parser.add_argument('--match-lang', type=str, metavar='STRING', default='de',
                        help='The Wikipedia language code for title matches (default: de).')
    parser.add_argument('--output-url-file', type=str, metavar='STRING',
                        help='The output file for the tsv with added URL for corresponding articles in other language.')
    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):
    # parsing the documents and writing to a tsv file
    spacy_model = spacy.load('en_core_web_sm') if args.input_lang.upper() == 'EN' else spacy.load('de_core_news_sm')
    databank_login = {'user':args.db_user, 'host':args.db_host, 'database':args.db_database}
    doc_parser = DocumentParser(spacy_model,
                                args.input,
                                args.match,
                                match_lang=args.match_lang,
                                no_match_file=args.no_match,
                                mysql_dict=databank_login,
                                n_processes=args.processes,
                                n_files=args.files,
                                verbose=args.verbose)
    doc_parser.parse_documents()

    # adding a column with URLs of articles in the other language
    finder = URLFinder(verbose=args.verbose)
    finder.create_url_dict(args.input_urls)
    finder.add_url_column(args.match, 7, args.output_url_file)
        

if __name__ == '__main__':
    args = parse_args()
    main(args)
