#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import os
import pandas as pd
import re
import sys

from typing import Dict


class URLFinder(object):
    def __init__(self, verbose: int = 1):
        """
        Args:
        verbose     the verbosity level.
        """
        self.verbose = verbose
        self.all_files = None
        self.column_idx = None
        self.df = None
        self.df_url = None
        self.document_dir = None
        self.input_file = None
        self.url_dict = None

    def create_url_dict(self, document_dir: str):
        """
        Creates a dictionary containing the URL for every title of an article in @param document_dir.

        Args:
        input_dir   a directory containing files in the medialab document format.
                        http://medialab.di.unipi.it/wiki/Document_Format
        """
        self.document_dir = document_dir
        self.all_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.document_dir)
            for file in files
        ]
        self._debug(f"Number of files found:\t{len(self.all_files)}")
        self._debug("Extracting URLs from files...")
        result_list = []
        for file in self.all_files:
            result = self._find_title_url(file)
            result_list += [result]
        self.url_dict = {key: value for d in result_list for key, value in d.items()}
        self._debug(f"Sucessfully extracted the URLs for {len(self.url_dict)} articles.")

    def add_url_column(self, input_file: str, column_idx: int, output_file: str):
        """
        Adds a column containing the URLs for every title in a specified (by index) column.

        Args:
        input_file      the name of a tsv file containig a column of article title to be mapped to URLs.
        column_idx      the index of the column containing the article titles.
        output_file     the output file where the new file will be saved.
        """
        self._debug(f"Adding a column with URLs and saving to {output_file}...")
        self.input_file = input_file
        self.column_idx = column_idx
        self.output_file = output_file
        self.df = pd.read_csv(input_file, sep="\t", quotechar='"', header=None)
        url_list = []
        warned = []
        for _, row in self.df.iterrows():
            try:
                url_list.append(self.url_dict[row[column_idx]])
            except KeyError:
                url_list.append("NOT_FOUND")
                if row[column_idx] not in warned:
                    self._debug(
                        f'Could not find the URL for article title "{row[column_idx]}".',
                        prefix="WARNING:\t",
                    )
                    warned.append(row[column_idx])
        self.df_url = self.df.copy()
        self.df_url.insert(column_idx + 1, column_idx + 1, pd.Series(url_list))
        self.df_url.to_csv(output_file, sep="\t", quotechar='"', index=False, header=False)
        self._debug(f"Failed to find URLs for {len(warned)} articles.", prefix="WARNING\t")
        self._debug(f"Task completed and output saved to {output_file}.")

    def _find_title_url(self, doc_file: str) -> Dict[str, str]:
        """
        Searches a file in medialab document format and returns a dictionary with article
        names as keys and URLs as values.
        """
        with open(doc_file, encoding="utf8") as infile:
            part_dict = {}
            for line in infile:
                if line.startswith("<doc id="):
                    head = line.lstrip("<doc ").rstrip(">")
                    title = re.search(r'title=(.*")', head).group(1).strip('"')
                    url = re.search(r"url=(\S*) ", head).group(1).strip('"')
                    part_dict[title] = url
        return part_dict

    def _debug(
        self,
        message: str,
        level: int = 1,
        prefix: str = "INFO:\t",
        spacing: str = "",
        end_spacing: str = "",
    ):
        """
        prints debug messages according to the verbosity level.
        """
        if self.verbose >= level:
            output = sys.stderr if not self.verbose > 50 else sys.stdout
            print(spacing + prefix + message + end_spacing, file=output)
