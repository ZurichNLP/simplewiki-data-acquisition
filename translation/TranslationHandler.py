#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import pandas as pd
import sys


class TranslationHandler(object):
    def __init__(self, verbose: int = 1):
        """
        Args:
        verbose     the verbosity level.
        """
        self.verbose = verbose
        self.source_df = None
        self.api_connector = None
        self.translations = None
        self.translations_col_idx = None
        self.translations_trg_lan = None

    def read_tsv(self, file_path: str):
        """
        Reads a tsv file containing a column of data ready for translation into a DataFrame.

        Args:
        file_path   the name of the input file.
        """
        self.source_df = pd.read_csv(file_path, sep="\t", quotechar='"', header=None)
        self._debug(f"Sucessfully read file {file_path}.")

    def translate_column(
        self,
        col_idx: int,
        api_connector,  # implements translate_sentences(sents: List[str], source_lang: str, target_lang: str).
        source_lang: str,
        target_lang: str,
    ):
        """
        Translates the content of a column from a provided source language into a provided target language
        using an @param api_connector.


        Args:
        col_idx             the column index in the DataFrame of the column to be translated.
        api_connector       an instance that performs the translation. must implement a translate_sentences
                                method that takes 3 arguments (sents: List[str], source_lang: str, target_lang: str)
                                and returns a list of sentences.
        source_lang         the source language.
        target_lang         the target language.
        """
        self.api_connector = api_connector
        sents = list(self.source_df.iloc[:, col_idx])
        self.translations = api_connector.translate_sentences(sents, "EN", "DE")
        self.translations_col_idx = col_idx
        self.translations_trg_lan = target_lang
        self._debug(f"Sucessfully translated {len(sents)} sentences.")

    def write_parallel_file(self, outpath: str):
        """
        Writes a parallel tsv file to the specified @param outpath containing source sentences and their
        respective translations.

        Args:
        outpath     the filename of the output file.
        """
        parallel_df = pd.DataFrame(self.source_df.iloc[:, self.translations_col_idx])
        parallel_df.insert(1, self.translations_trg_lan, pd.Series(self.translations))
        parallel_df.to_csv(outpath, sep="\t", quotechar='"', index=False, header=False)
        self._debug(
            f"Parallel file with original sentences and translations was written to {outpath}."
        )

    def add_translation_column(self, outpath: str):
        """
        Writes a copy of the original file with an added column containing the translations to the
        specified @param outpath.

        Args:
        outpath     the filename of the output file.
        """
        all_df = self.source_df.copy()
        all_df.insert(len(all_df.columns), self.translations_trg_lan, pd.Series(self.translations))
        all_df.to_csv(outpath, sep="\t", quotechar='"', index=False, header=False)
        self._debug(
            f"A column with translations was added to the original file and written to {outpath}."
        )

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
