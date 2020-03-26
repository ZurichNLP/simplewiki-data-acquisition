#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import csv
import mysql.connector
import os
import pathos.multiprocessing as mp
import re
import spacy
import sys

from typing import Dict, List, Optional, Tuple


class DocumentParser(object):

    def __init__(self, model: "spacy model for any given language.",
                       input_dir: str,
                       match_file: str,
                       match_lang: str = None,
                       no_match_file: str = None,
                       mysql_dict: Dict = None,
                       n_processes: int = mp.cpu_count(),
                       n_files: int = 1,
                       verbose: int = 1):
        '''
        Args:
        model           a spacy model used to tokenize text into sentences.
        input_dir       a directory containing files in the medialab document format.
                            http://medialab.di.unipi.it/wiki/Document_Format
        match_file      output file for articles with a match. if no @param match_lang is provided,
                            all output will be written to this file.
        match_lang      the wikipedia language code for which titles will be queried in the langlinks table.
        no_match_file   output file for articles with no match.
        mysql_dict      a dictionary containing arguments for the mysql.connector used to access the langlinks table
                            in a mysql databank.
        n_processes     the number of parallel processes to be run.
        n_files         the number of files handled per process before writing to the output file.
        verbose         the verbosity level.
        '''
        self.model = model
        self.input_dir = input_dir
        self.match_file = match_file
        self.match_lang = match_lang
        self.no_match_file = no_match_file
        self.mysql_dict = mysql_dict
        self.n_processes = n_processes
        self.n_files = n_files
        self.verbose = verbose
        self.chunks = None
        self.all_files = None

        self.find_corresponding_article_title = self.match_lang is not None

        # checking arguments
        if self.find_corresponding_article_title:
            self._debug('@param match_lang has been provided. Article titles will be looked up in the langlinks table.')
            self._debug('Arguments required for this: no_match_file, mysql_dict.')
            assert self.no_match_file is not None and self.mysql_dict is not None
            self._debug('Testing access to the langlinks table...')
            cnx = mysql.connector.connect(**self.mysql_dict)
            cnx.close()
            self._debug('langlinks table can be accessed.')

        # emptying output files
        open(self.match_file, 'w').close()
        if self.find_corresponding_article_title:
            open(no_match_file, 'w').close()

    def parse_documents(self) -> Dict[str, int]:
        '''
        parses the documents and writes the parsed line into tsv files.
        '''
        self._create_chunks()
        done = 0
        match_results = []
        no_match_results = []
        for chunk in self.chunks:
            with mp.Pool(processes=self.n_processes) as pool:
                results = pool.starmap_async(self._parse_document_file, [(file,) for file in chunk])
                results = results.get()
            for file in results:
                match_results += file[0]
                no_match_results += file[1]
            self._write_output_tsv(self.match_file, match_results)
            if self.find_corresponding_article_title:
                self._write_output_tsv(self.no_match_file, no_match_results)
            match_results = []
            no_match_results = []
            done += len(chunk)
            self._debug(f'Parsed {done}/{len(self.all_files)} files.')
        column_dict = {'article_id':0,
                       'section_id':1,
                       'sent_id':2,
                       'orig_url':3,
                       'orig_title':4,
                       'orig_section':5,
                       'orig_sent':6,
                       'other_title':7}
        return column_dict

    def _create_chunks(self):
        '''
        creates chunks of file names of size n_processes*n_files.
        '''
        self.all_files = [os.path.join(root, file) for root, _, files in os.walk(self.input_dir) for file in files]
        self._debug(f'Number of files found:\t{len(self.all_files)}')
        self._debug(f'Trying to create chunks of size {self.n_processes*self.n_files} ' + \
                    f'({self.n_files} file(s) each for {self.n_processes} processes)...')
        chunk_size = self.n_processes * self.n_files
        self.chunks = [self.all_files[i * chunk_size:(i+1) * chunk_size]
                      for i in range((len(self.all_files) + chunk_size - 1) // chunk_size)]
        self._debug(f'Created {len(self.chunks)} chunk(s).')

    def _parse_document_file(self, doc_file: str) -> Tuple[List[Tuple[str]], List[Tuple[str]]]:
        '''
        extracts lines and metadata from raw articles and generates lines ready for output.
        '''
        cnx = mysql.connector.connect(**self.mysql_dict) if self.find_corresponding_article_title else None
        cursor = cnx.cursor() if self.find_corresponding_article_title else None
        articles = self._extract_articles(doc_file)
        match_lines, no_match_lines = self._generate_lines(articles, self.model, self.match_lang, cursor)
        if self.find_corresponding_article_title:
            cursor.close()
            cnx.close()
        return match_lines, no_match_lines

    def _extract_articles(self, doc_file: str) -> List[Tuple[Dict[str, str], str]]:
        '''
        opens a file in medialab document format and returns tuples of metadata and lines
        '''
        with open(doc_file, encoding='utf8') as infile:
            articles = []
            contents = ''
            attributes = {}
            for line in infile:
                if line.startswith('</doc>'):
                    articles.append(({**attributes}, contents))
                    contents = ''
                elif line.startswith('<doc '):
                    head = line.lstrip('<doc ').rstrip('>')
                    attributes['id'] = re.search(r'id=(\S*) ', head).group(1).strip('"')
                    attributes['url'] = re.search(r'url=(\S*) ', head).group(1).strip('"')
                    attributes['title'] = re.search(r'title=(.*")', head).group(1).strip('"')
                else:
                    contents += line
        return articles

    def _generate_lines(self,
                        articles: List[Tuple[Dict[str, str], str]],
                        model: "spacy model for any given language.",
                        match_lang: str,
                        cursor: mysql.connector.cursor_cext.CMySQLCursor) -> Tuple[List[Tuple[str]], List[Tuple[str]]]:
        '''
        generates tuples representing lines in a final output file
        '''
        match_lines = []
        no_match_lines = []
        for attrs, text in articles:
            lines = []
            section_name = 'Summary'
            section_id = 1
            sent_id = 1
            for line in text.split('\n'):
                # filtering out empty lines and the title line
                if not line.startswith('\n') and not line == attrs['title']:
                    # the beginning of a new section
                    if line.startswith('Section::::'):
                        section_id += 1
                        section_name = line.replace('Section::::', '').rstrip('.')
                    # normal text rows
                    else:
                        doc = model(line)
                        for sent in doc.sents:
                            sent = str(sent)
                            lin = [attrs['id'], section_id, sent_id, attrs['url'], 
                                   attrs['title'], section_name, sent]
                            lines.append(lin)
                            sent_id += 1
            if self.find_corresponding_article_title:
                matched_title = self._find_other_lang_title(attrs['id'], cursor, match_lang)
                if matched_title:
                    match_lines += [tuple(l + [matched_title]) for l in lines]
                else:
                    no_match_lines += [tuple(l) for l in lines]
            else:
                match_lines += [tuple(l) for l in lines]
        return match_lines, no_match_lines

    def _find_other_lang_title(self,
                               article_id: str,
                               cursor: mysql.connector.cursor_cext.CMySQLCursor,
                               match_lang: str) -> Optional[str]:
        '''
        queries the langlinks table for the title of a specific article in another language
        '''
        query = "SELECT * FROM langlinks WHERE ll_from = %s AND ll_lang = %s"
        cursor.execute(query, (article_id, match_lang))
        results = cursor.fetchall()
        return results[0][2] if len(results) > 0 else None

    def _write_output_tsv(self, outfile: str, lines: List[Tuple[str]]):
        '''
        writes the tuples (each representing a line) in a list into a tsv
        '''
        with open(outfile, 'a', encoding='utf8') as outfile:
            writer = csv.writer(outfile, delimiter='\t', quotechar='"')
            for line in lines:
                writer.writerow(line)

    def _debug(self, message: str, level: int = 1, prefix: str = 'INFO:\t', spacing: str = '', end_spacing: str = ''):
        '''
        prints debug messages according to the verbosity level.
        '''
        if self.verbose >= level:
            output = sys.stderr if not self.verbose > 50 else sys.stdout
            print(spacing + prefix + message + end_spacing, file=output)
