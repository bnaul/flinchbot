"""`main` is the top level module for your Flask application."""

from __future__ import absolute_import, division, print_function

import logging

from flask import Flask, request, jsonify

import json
import random
import re
from urllib import urlencode
from urllib2 import urlopen
from markovgen import markovgen

app = Flask(__name__)

#DATA_FILE = 'gato_combined.txt'
DATA_FILE = 'flinch_slack.txt'
CHAIN_LEN = 3
MIN_WORDS = 4
MAX_WORDS = 16


@app.route('/', methods=['GET'])
def index():
    markov = markovgen(DATA_FILE, CHAIN_LEN)
    num_words = random.randint(MIN_WORDS, MAX_WORDS)
    if 'text' in request.args and len(request.args['text'].strip()) > 0:
        seed = request.args['text']
    else:
        seed = None
    try:
        resp = markov.generate_markov_text(num_words, seed)
        resp_dict = {
                "response_type": "in_channel",
                "text": resp
        }

        if '/giphy' in resp.lower():
            start = resp.lower().find('/giphy') + len('/giphy')
            match = re.search('[.!?/]', resp[start:])
            if match:
                end = start + match.start()
            else:
                end = None
            query = resp[start:end]
            search_string = urlencode({'tag': query, 'api_key': 'dc6zaTOxFJmzC'})
            try:
                giphy = urlopen('http://api.giphy.com/v1/gifs/random?' + search_string)
                gif_url = json.load(giphy)['data']['image_url']
                resp_dict['attachments'] = [{'image_url': gif_url, 'text': query}]
            except Exception as e:
                logging.warning(str(e))
    except:
        resp_dict = {
                "response_type": "ephemeral",
                "text": "Search term not found."
        }


    return jsonify(**resp_dict)

