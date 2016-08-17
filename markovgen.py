import os
import random
import re
from argparse import ArgumentParser


# After num_words, we keep going until we reach the end of a sentence
STOP_TOKEN = '_____'


class markovgen(object):
    def __init__(self, filename, chain_len):
        self.chain_len = chain_len
        lines = [l.rstrip() for l in open(filename).readlines()]
        lines = [s for l in lines for s in re.split(r' *[\.\?!][\'"\)\]]* *', l)]
        lines = [l for l in lines if len(l) > 0]
        for i in range(len(lines)):
            if lines[i][-1].isalnum():
                lines[i] += '.'
            lines[i] += ' ' + STOP_TOKEN
        words = [STOP_TOKEN] + [w for l in lines for w in l.split()]

        self.database = self.build_database(words, self.chain_len)
        self.reversed = self.build_database(list(reversed(words)), self.chain_len)

    def build_database(self, words, chain_len):
        database = {}
        for chain in [words[i:i+(chain_len)] for i in range(len(words) - (chain_len - 1))]:
            key = tuple(chain[:-1])
            if key not in database:
                database[key] = []
            database[key].append(chain[-1])
        return database

    def add_word(self, words, db=None):
        if db is None:
            db = self.database
        if tuple(words[-(self.chain_len-1):]) in db:
            words.append(random.choice(db[tuple(words[-(self.chain_len-1):])]))
# Sometimes we get stuck (e.g. the words at the very end of the corpus); just choose randomly
        else:
            words.append(random.choice(db.keys())[0])

    def generate_markov_text(self, num_words, seed=None):
        if seed:
            matches = filter(lambda key: all(w.lower() in key for w in seed.split())
                             or all(w in key for w in seed.split())
                             or all(w.capitalize() in key for w in seed.split()),
                             self.reversed.keys())
            if len(matches) > 0:
                words = list(random.choice(matches))
            else:
                raise ValueError("Not found.")
        else:
            words = list(random.choice(self.database.keys()))
        while not STOP_TOKEN in words:
            self.add_word(words, db=self.reversed)
        words = [w for w in reversed(words) if w != STOP_TOKEN]
        for i in range(num_words):
            self.add_word(words)
        while not STOP_TOKEN in words:
            self.add_word(words)
        words[0] = words[0].capitalize()
        text = ' '.join(words)
        text = re.sub(STOP_TOKEN, '', text)
        text = re.sub('\n', ' ', text)
        text = re.sub('  *', ' ', text)
        return text


def main():
    parser = ArgumentParser()
    parser.add_argument('-n', '--num_words', dest='num_words', type=int, default=20)
    parser.add_argument('-c', '--chain_len', dest='chain_len', type=int, default=3)
    parser.add_argument('-s', '--seed', dest='seed')
    parser.add_argument('-f', '--file', dest='filename', default='/dev/stdin')
    values = parser.parse_args()

    markov = markovgen(values.filename, values.chain_len)
    text = markov.generate_markov_text(values.num_words, values.seed)
    print text

if __name__ == '__main__':
    main()
