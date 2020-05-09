#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import argparse
import csv
import io
import re
import sys

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=argparse.FileType('r'),
                        help='input file (default: stdin)',
                        default=sys.stdin, metavar='PATH')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        help='output file (default: stdout)',
                        default=sys.stdout, metavar='PATH')
    args = parser.parse_args()
    return args


def extract_images_from_xml_dump(infile: '_io.TextIOWrapper', outfile: '_io.TextIOWrapper'):
    '''
    extracts article titles, links and image captions for all image in a Wikipedia dump XML file.

    Args:
        infile      xml input file
        outfile     csv output file
    '''
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    url_prefix = 'https://simple.wikipedia.org/wiki/'
    current_article = ''
    last_line = ''
    for line in infile:
        line = line.strip()
        if line.startswith('<title>') and last_line == '<page>':
            current_article = line[7:-8]
        elif '[[File:' in line:
            filename = re.search(r'\[\[((?:File|Image):[^|]*)', line).group(1)
            rest = re.search(r'\[\[(?:File|Image):[^|]*(.*$)', line).group(1)
            caption = clean_caption(extract_caption(rest))
            if caption:
                writer.writerow([current_article, url_prefix+filename, caption])
        last_line = line


def extract_caption(line: str) -> str:
    '''
    extracts the last field (potential image caption) of an input string of form "text|text|text]]"

    Args:
        line    the input line

    Returns:
                the last field
    '''
    brackets = 2
    curr_field = ''
    for char in line:
        if char == ']':
            brackets -= 1
            if brackets == 0:
                return curr_field
        elif char == '[':
            brackets += 1
        elif char == '|':
            curr_field = ''
        else:
            curr_field += char
    return ''


def clean_caption(caption: str) -> str:
    '''
    cleans a potential caption by removing double brackets and other parameters for images
    which have no caption.

    Args:
        caption     a potential image caption

    Returns:
                    the cleaned caption
    '''
    non_captions = ['px', 'thumb', 'frameless', 'center', 'left', 'right']
    for ending in non_captions:
        if caption.endswith(ending):
            return ''
    return caption.replace('[', '').replace(']', '')


def main(args: argparse.Namespace):
    extract_images_from_xml_dump(args.input, args.output)
        

if __name__ == '__main__':
    args = parse_args()
    main(args)
