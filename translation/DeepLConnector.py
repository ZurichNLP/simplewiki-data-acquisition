#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import requests
import sys
import urllib

from typing import List

class DeepLConnector(object):

    def __init__(self, auth_key: str, save_path: str = None, verbose: int = 1):
        '''
        Args:
        auth_key    the authentification key to access the DeepL API.
        verbose     the verbosity level.
        '''
        self.url = 'https://api.deepl.com/v2/translate'
        self.save_path = save_path
        self.verbose = verbose
        self.__auth_key = auth_key

    def translate_sentences(self, sents: List[str], source_lang: str, target_lang: str) -> List[str]:
        '''
        creates chunks of 25 sentences each and translates them using the DeepL API v2.

        Args:
        sents       a list of sentences to be translated.
        source_lang the source language.
        target_lang the target language.

        Returns:
        translated_sents    a list of translated sentences.
        '''
        self._debug(f'Sentences to translate: {len(sents)}')
        open(self.save_path, 'w').close()
        prog_info_every = len(sents) // 100 if len(sents) // 100 >= 1 else 1
        done = 0
        reached = set()
        translated_sents = []
        chunk_size = 25
        sent_chunks = [sents[i * chunk_size:(i+1) * chunk_size] for i in range((len(sents) + chunk_size - 1) // chunk_size)]
        key = 'auth_key=' + self.__auth_key
        source = 'source_lang=' + source_lang
        target = 'target_lang=' + target_lang
        splitting = 'split_sentences=0'
        for chunk in sent_chunks:
            response = self._make_request(chunk, key, source, target, splitting)
            if response.status_code == 414:
                self._debug(f'414 URI Too Long.', prefix='WARNING:\t')
                self._debug(f'Sending sentences of this chunk one by one...', prefix='WARNING:\t')
                tr_sents = []
                for sent in chunk:
                    response = self._make_request([sent], key, source, target, splitting)
                    json = response.json()
                    tr_sents += [entry['text'] for entry in json['translations']]
                self._debug(f'Done, resuming normal operation...', prefix='WARNING:\t')
            else:
                json = response.json()
                tr_sents = [entry['text'] for entry in json['translations']]
            translated_sents += tr_sents
            if self.save_path:
                with open(self.save_path, 'a', encoding='utf8') as outfile:
                    for sent in tr_sents:
                        outfile.write(sent + '\n')
            done += len(chunk)
            last = done - (done % prog_info_every)
            if last not in reached and last != 0:
                self._debug(f'Translated {last}/{len(sents)} sentences.')
                reached.add(last)
        return translated_sents

    def _make_request(self, chunk: List[str], key: str, source: str, target: str, splitting: str) -> requests.models.Response:
        '''
        makes a request to the DeepL API v2 translating the sentences in @param chunk
        and returns a requests.models.Response.
        '''
        sent_chunk = 'text=' + '&text='.join([urllib.parse.quote(sent) for sent in chunk])
        get_url = '&'.join(['?'.join([self.url, key]), sent_chunk, source, target, splitting])
        response = requests.get(get_url)
        self._debug(f'{response}', level=11)
        return response

    def _debug(self, message: str, level: int = 1, prefix: str = 'INFO:\t', spacing: str = '', end_spacing: str = ''):
        '''
        prints debug messages according to the verbosity level.
        '''
        if self.verbose >= level:
            output = sys.stderr if not self.verbose > 50 else sys.stdout
            print(spacing + prefix + message + end_spacing, file=output)
