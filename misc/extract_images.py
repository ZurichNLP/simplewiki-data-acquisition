#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import argparse
import csv
import re
import sys

from typing import List, IO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        type=argparse.FileType("r"),
        help="input file (default: stdin)",
        default=sys.stdin,
        metavar="PATH",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("w"),
        help="output file (default: stdout)",
        default=sys.stdout,
        metavar="PATH",
    )
    parser.add_argument(
        "-n-neighbors",
        type=int,
        default=10,
        help="number of neighboring lines to search for sentences (default: 10)",
    )
    args = parser.parse_args()
    return args


class FileWindow(object):
    """
    helper class to keep track of neighboring lines in a file. returns lists with a flexible amount
    of lines before and after the current line in the file.

    return format ('line4' ist the current line):
        tuple(['line1', 'line2', 'line3'], 'line4', ['line5', 'line6', 'line7'])
        the window is being padded with None at the beginning and end of the file.
    """

    def __init__(self, infile: IO, window_size: int = 10):
        """
        infile          file to loop over
        window_size     number of lines in each direction to return with the current line
        """
        self.__infile = infile
        self.__window_size = window_size
        self.__initialize_window()

    def __initialize_window(self):
        self.window = [None for _ in range(2 * self.__window_size + 1)]
        for n, line in enumerate(self.__infile):
            self.window[self.__window_size + n] = line
            if n == self.__window_size:
                break

    def __iter__(self):
        return self

    def __next__(self):
        if not self.window[self.__window_size] is None:
            prev = self.window[: self.__window_size]
            curr = self.window[self.__window_size]
            later = self.window[self.__window_size + 1 :]
            self.window.pop(0)
            try:
                self.window.append(next(self.__infile))
            except StopIteration:
                self.window.append(None)
            return prev, curr, later
        else:
            raise StopIteration


def extract_images_from_xml_dump(infile: IO, outfile: IO, neighboring_lines: int = 10):
    """
    extracts article titles, links and image captions for all image in a Wikipedia dump XML file.

    Args:
        infile              xml input file
        outfile             csv output file
        neighboring_lines   max number of neighboring lines to an image to search for text
    """
    writer = csv.writer(outfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    url_prefix = "https://simple.wikipedia.org/wiki/"
    current_id = ""
    current_article = ""
    current_section = ""
    last_line = ""
    for before, line, after in FileWindow(infile, neighboring_lines):
        line = line.strip()
        # beginning of a new article
        if line.startswith("<title>") and last_line == "<page>":
            current_article = line[7:-8]
            current_section = "Summary"
        # extracting article IDs
        if line.startswith("<id>") and last_line.startswith("<ns>"):
            current_id = line[4:-5]
        # beginning of a new section
        elif line.startswith("== "):
            current_section = line[3:-3]
        # images
        elif "[[File:" in line:
            filename = re.search(r"\[\[((?:File|Image):[^|]*)", line).group(1)
            rest = re.search(r"\[\[(?:File|Image):[^|]*(.*$)", line).group(1)
            caption = clean_caption(extract_caption(rest))
            if caption:
                sents_before = "\n".join(find_neighboring_sents_in_section(before, "previous"))
                sents_after = "\n".join(find_neighboring_sents_in_section(after, "later"))
                writer.writerow(
                    [
                        current_id,
                        current_article,
                        current_section,
                        url_prefix + filename,
                        caption,
                        sents_before,
                        sents_after,
                    ]
                )
        last_line = line


def find_neighboring_sents_in_section(lines: List[str], mode: str = "previous") -> List[str]:
    """
    finds text sentences that still belong to the same section in the article. argument
    "mode" can be used to control the direction of list traversal:
        -> 'previous' starts at the last element of the list and stops at a section marker
        -> 'later' starts at the first element of the list and stops at a section marker

    Args:
        lines   a list of lines
        mode    'previous' or 'later', controls the direction of list traversal

    Returns:
        sents   a list of cleaned sentences
    """
    assert mode == "previous" or mode == "later"
    length = len(lines)
    pos = length - 1 if mode == "previous" else 0
    sents = []
    while (mode == "previous" and pos != -1) or (mode == "later" and pos != length):
        if lines[pos] is None:
            break
        line = lines[pos].strip()
        # section marker or beginning of article
        if line.startswith("== ") or line.startswith("<"):
            break
        if valid_line(line):
            sents.append(line.replace("[", "").replace("]", ""))
        pos = pos - 1 if mode == "previous" else pos + 1
    return sents[::-1] if mode == "previous" else sents


def valid_line(line: str) -> bool:
    """
    checks if a line not invialid (part of XML structure, tables, figures etc.)

    Returns:
            whether or not the input is a valid line
    """
    if line:
        invalid_starts = ["|", "=", "[", "]", "<", ">", "{", "}", "**", "*"]
        for elem in invalid_starts:
            if line.startswith(elem):
                return False
        return True
    return False


def extract_caption(line: str) -> str:
    """
    extracts the last field (potential image caption) of an input string of form "text|text|text]]"

    Args:
        line    the input line

    Returns:
                the last field
    """
    brackets = 2
    curr_field = ""
    for char in line:
        if char == "]":
            brackets -= 1
            if brackets == 0:
                return curr_field
        elif char == "[":
            brackets += 1
        elif char == "|":
            curr_field = ""
        else:
            curr_field += char
    return ""


def clean_caption(caption: str) -> str:
    """
    cleans a potential caption by removing double brackets and other parameters for images
    which have no caption.

    Args:
        caption     a potential image caption

    Returns:
                    the cleaned caption
    """
    non_captions = ["px", "thumb", "frameless", "center", "left", "right"]
    for ending in non_captions:
        if caption.endswith(ending):
            return ""
    return caption.replace("[", "").replace("]", "")


def main(args: argparse.Namespace):
    extract_images_from_xml_dump(args.input, args.output, args.n_neighbors)


if __name__ == "__main__":
    args = parse_args()
    main(args)
