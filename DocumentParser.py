#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import argparse
import csv
import os
import re
import spacy
import sys
import pathos.multiprocessing as mp
import mysql.connector


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str,
                        help='a folder the WikiExtractor outputs.',
                        metavar='PATH', required=True)
    parser.add_argument('-m', '--match', type=str,
                        help='output file for articles with a match. ' +\
                        'If no --match-lang is provided, all output will be written to this file.',
                        metavar='PATH', default=sys.stdout)
    parser.add_argument('-n', '--no-match', type=str,
                        help='output file for articles with no match.',
                        metavar='PATH', default=None)
    parser.add_argument('-p', '--processes', type=int,
                        help='the number of processes to be run in parallel.',
                        default=mp.cpu_count(), metavar='INT')
    parser.add_argument('-f', '--files', type=int,
                        help='the number of files handled per process before writing to the output file.',
                        default=1, metavar='INT')
    parser.add_argument('--input-lang', type=str, metavar='STRING',
                        help='the language of the input files (en/de)',
                        choices=['de', 'en'], default='en')
    parser.add_argument('--match-lang', type=str, metavar='STRING', default=None,
                        help='the Wikipedia language code for title matches.')
    parser.add_argument('--db-user', type=str, metavar='STRING',
                        help='the mysql databank user with access to the langlinks table.')
    parser.add_argument('--db-host', type=str, metavar='STRING',
                        help='the host of the databank containing the langlinks table.')
    parser.add_argument('--db-database', type=str, metavar='STRING',
                        help='the mysql database containing the langlinks table.')
    parser.add_argument('-v' ,'--verbose', type=int, metavar='INT',
                        help='the verbosity level of the DocumentParser.', default=1)
    args = parser.parse_args()
    return args


class DocumentParser(object):

    def __init__(self, model,
                       input_dir,
                       match_file,
                       match_lang=None,
                       no_match_file=None,
                       mysql_dict=None,
                       n_processes=mp.cpu_count(),
                       n_files=1,
                       verbose=1):
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


    def parse_documents(self):
        '''
        parses the documents and writes the parsed line into tsv files.
        '''
        self._create_chunks()
        done = 0
        match_results = []
        no_match_results = []
        for chunk in self.chunks:
            with mp.Pool(processes=self.n_processes) as pool:
                results = pool.starmap(self._parse_document_file, [(file,) for file in chunk])
            for file in results:
                match_results += file[0]
                no_match_results += file[1]
            self._write_output_tsv(self.match_file, match_results)
            if self.find_corresponding_article_title:
                self._write_output_tsv(self.no_match_file, no_match_results)
            done += len(chunk)
            self._debug(f'Parsed {done}/{len(self.all_files)} files.')


    def _create_chunks(self):
        '''
        creates chunks of file names of size n_processes*n_files.
        '''
        self.all_files = [os.path.join(root, file) for root, _, files in os.walk(self.input_dir) for file in files]
        self._debug(f'Number of files found:\t{len(self.all_files)}', spacing='\n'*3)
        self._debug(f'Trying to create chunks of size {self.n_processes*self.n_files} ' + \
                    f'({self.n_files} file(s) each for {self.n_processes} processes)...')
        chunk_size = self.n_processes * self.n_files
        self.chunks = [self.all_files[i * chunk_size:(i+1) * chunk_size]
                      for i in range((len(self.all_files) + chunk_size - 1) // chunk_size)]
        self._debug(f'Created {len(self.chunks)} chunk(s).')


    def _parse_document_file(self, doc_file):
        '''
        extracts lines and metadata from raw articles and generates lines ready for output.
        '''
        cnx = mysql.connector.connect(**self.mysql_dict)
        cursor = cnx.cursor()
        articles = self._extract_articles(doc_file)
        match_lines, no_match_lines = self._generate_lines(articles, self.model, self.match_lang, cursor)
        cursor.close()
        cnx.close()
        return match_lines, no_match_lines


    def _extract_articles(self, doc_file):
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


    def _generate_lines(self, articles, model, match_lang, cursor):
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


    def _find_other_lang_title(self, article_id, cursor, match_lang):
        '''
        queries the langlinks table for the title of a specific article in another language
        '''
        query = "SELECT * FROM langlinks WHERE ll_from = %s AND ll_lang = %s"
        cursor.execute(query, (article_id, match_lang))
        results = cursor.fetchall()
        return results[0][2] if len(results) > 0 else None


    def _write_output_tsv(self, outfile, lines):
        '''
        writes the tuples (each representing a line) in a list into a tsv
        '''
        if outfile != sys.stdout:
            with open(outfile, 'w', encoding='utf8') as outfile:
                writer = csv.writer(outfile, delimiter='\t', quotechar="'")
                for line in lines:
                    writer.writerow(line)
        else:
            writer = csv.writer(outfile, delimiter='\t', quotechar="'")
            for line in lines:
                writer.writerow(line)


    def _debug(self, message, level=1, prefix='INFO:\t', spacing='', end_spacing=''):
        '''
        prints debug messages according to the verbosity level.
        '''
        if self.verbose >= level:
            output = sys.stderr if not self.verbose > 50 else sys.stdout
            print(spacing + prefix + message + end_spacing, file=output)

    

def main(args: argparse.Namespace):
    spacy_model = spacy.load('en_core_web_sm') if args.input_lang == 'en' else spacy.load('de_core_news_sm')
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



        

if __name__ == '__main__':
    args = parse_args()
    main(args)
