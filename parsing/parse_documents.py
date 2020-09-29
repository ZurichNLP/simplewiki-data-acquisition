#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import argparse
import pathos.multiprocessing as mp

from DocumentParser import DocumentParser
from URLFinder import URLFinder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--files",
        type=int,
        metavar="INT",
        default=1,
        help="The number of files handled per process before writing to the output file.",
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        metavar="PATH",
        required=True,
        help="A directory containing files in medialab document format for parsing.",
    )
    parser.add_argument(
        "-m",
        "--match",
        type=str,
        metavar="PATH",
        help="Output file for articles with a match. "
        + "If no --match-lang is provided, all output will be written to this file.",
    )
    parser.add_argument(
        "-n",
        "--no-match",
        type=str,
        metavar="PATH",
        default=None,
        help="Output file for articles with no match.",
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        metavar="INT",
        default=mp.cpu_count(),
        help="The number of processes to be run in parallel.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        metavar="INT",
        default=1,
        help="The verbosity level of the DocumentParser.",
    )
    parser.add_argument(
        "--db-user",
        type=str,
        metavar="STRING",
        help="The mysql databank user with access to the langlinks table.",
    )
    parser.add_argument(
        "--db-database",
        type=str,
        metavar="STRING",
        help="The mysql database containing the langlinks table.",
    )
    parser.add_argument(
        "--db-host",
        type=str,
        metavar="STRING",
        help="The host of the databank containing the langlinks table.",
    )
    parser.add_argument(
        "--input-lang",
        type=str,
        metavar="STRING",
        default="en",
        help="The language of the input files",
    )
    parser.add_argument(
        "--input-urls",
        type=str,
        metavar="STRING",
        help="A directory containing files in medialab document format for extracting other language URLs.",
    )
    parser.add_argument(
        "--match-lang",
        type=str,
        metavar="STRING",
        help="The Wikipedia language code for title matches.",
    )
    parser.add_argument(
        "--no-urls",
        action="store_true",
        help="Running the scripts in single language mode without URL lookups.",
    )
    parser.add_argument(
        "--output-url-file",
        type=str,
        metavar="STRING",
        help="The output file for the tsv with added URL for corresponding articles in other language.",
    )
    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):
    assert args.no_urls is True or bool(args.input_urls and args.output_url_file) is not False, (
        "URL extraction requires an input directory (arg --input-urls) and an output file (arg --output-url-file). "
        + "Use arg --no-urls to skip foreign URL extraction."
    )

    # parsing the documents and writing to a tsv file
    databank_login = {"user": args.db_user, "host": args.db_host, "database": args.db_database}
    doc_parser = DocumentParser(
        args.input,
        args.input_lang,
        args.match,
        match_lang=args.match_lang,
        no_match_file=args.no_match,
        mysql_dict=databank_login,
        n_processes=args.processes,
        n_files=args.files,
        verbose=args.verbose,
    )
    doc_parser.parse_documents()

    if not args.no_urls:
        # adding a column with URLs of articles in the other language
        finder = URLFinder(verbose=args.verbose)
        finder.create_url_dict(args.input_urls)
        finder.add_url_column(args.match, 7, args.output_url_file)


if __name__ == "__main__":
    args = parse_args()
    main(args)
