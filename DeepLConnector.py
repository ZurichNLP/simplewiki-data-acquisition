#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Nicolas Spring

import requests
import urllib

from typing import List

class DeepLConnector(object):

    def __init__(self, auth_key: str, verbose: int = 1):
        '''
        Args:
        auth_key    the authentification key to access the DeepL API.
        verbose     the verbosity level.
        '''
        self.url = 'https://api.deepl.com/v2/translate'
        self.verbose = verbose
        self.__auth_key = auth_key

    def translate_sentences(self, sents: List[str], source_lang: str, target_lang: str) -> List[str]:
        '''
        creates chunks of 50 sentences each and translates them using the DeepL API v2.

        Args:
        sents       a list of sentences to be translated.
        source_lang the source language.
        target_lang the target language.

        Returns:
        translated_sents    a list of translated sentences.
        '''
        prog_info_every = len(sents) // 100
        done = 0
        reached = set()
        translated_sents = []
        sent_chunks = [sents[i * 50:(i+1) * 50] for i in range((len(sents) + 50 - 1) // 50)]
        key = 'auth_key=' + self.__auth_key
        source = 'source_lang=' + source_lang
        target = 'target_lang=' + target_lang
        for chunk in sent_chunks:
            sent_chunk = 'text=' + '&text='.join([urllib.parse.quote(sent) for sent in chunk])
            get_url = '&'.join(['?'.join([self.url, key]), sent_chunk, source, target])
            response = requests.get(get_url)
            json = response.json()
            tr_sents = [entry['text'] for entry in json['translations']]
            translated_sents += tr_sents
            done += len(chunk)
            last = done - (done % prog_info_every)
            if last not in reached and last != 0:
                self._debug(f'Translated {last}/{len(sents)} sentences.')
                reached.add(last)
        return translated_sents

    def _debug(self, message: str, level: int = 1, prefix: str = 'INFO:\t', spacing: str = '', end_spacing: str = ''):
        '''
        prints debug messages according to the verbosity level.
        '''
        if self.verbose >= level:
            output = sys.stderr if not self.verbose > 50 else sys.stdout
            print(spacing + prefix + message + end_spacing, file=output)


def main():
    pass



if __name__ == '__main__':
    main()

