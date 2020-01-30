#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring


import argparse

from TranslationHandler import TranslationHandler
from DeepLConnector import DeepLConnector


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--column-index', type=int, default=6, metavar='INT',
                        help='An integer (starting at 0) signifying the index of the column' + \
                        'with the sentences for translation.')
    parser.add_argument('-i', '--input', type=str,
                        help='A tsv file containing a column of data ready for translation.',
                        metavar='PATH', required=True)
    parser.add_argument('-o', '--output', type=str,
                        help='The filename of the output file.',
                        metavar='PATH', required=True)
    parser.add_argument('-s', '--save-file', type=str, metavar='PATH', required=True,
                        help='File for saving copies of freshly translated sentences.')
    parser.add_argument('-v' ,'--verbose', type=int, metavar='INT',
                        help='The verbosity level.', default=1)
    parser.add_argument('--auth-key', type=str, metavar='STRING', required=True,
                        help='The authentication key for the DeepL API.')
    parser.add_argument('--source-lang', type=str, metavar='STRING', required=True,
                        help='DeepL API Code for the source language (EN/DE/FR/ES/PT/IT/NL/PL/RU)')
    parser.add_argument('--target-lang', type=str, metavar='STRING', required=True,
                        help='DeepL API Code for the target language (EN/DE/FR/ES/PT/IT/NL/PL/RU)')
    args = parser.parse_args()
    return args


def main(args: argparse.Namespace):
    api_connector = DeepLConnector(auth_key=args.auth_key, save_path=args.save_file, verbose=args.verbose)
    translation_handler = TranslationHandler(verbose=args.verbose)
    translation_handler.read_tsv(args.input)
    translation_handler.translate_column(args.column_index, api_connector, args.source_lang.upper(), args.target_lang.upper())
    translation_handler.add_translation_column(args.output)


if __name__ == '__main__':
    args = parse_args()
    main(args)
