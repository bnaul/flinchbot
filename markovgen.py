import os
import random
import re
from collections import defaultdict
from argparse import ArgumentParser


# After num_words, we keep going until we reach the end of a sentence
STOP_TOKEN = '_____'

PUNCTUATION = '.!?"\''


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
        self.key_list = defaultdict(list)
        for k in self.database.keys():
            for w in k:
                self.key_list[w.lower().strip(PUNCTUATION)].append(k)

    def build_database(self, words, chain_len):
        database = {}
        slices = (words[i:] for i in range(chain_len))
        for chain in zip(*slices):
            key = tuple(w.strip(PUNCTUATION) for w in chain[:-1])
            if key not in database:
                database[key] = []
            database[key].append(chain[-1])
        return database

    def add_word(self, words, db=None):
        if db is None:
            db = self.database
        current_chain = tuple(w.strip(PUNCTUATION) for w in words[-(self.chain_len-1):])
        if current_chain in db:
            next_word = random.choice(db[current_chain])
        # Sometimes we get stuck (e.g. the words at the very end of the corpus); choose randomly
        else:
            raise
            next_word = STOP_TOKEN
            #next_word = random.choice(random.choice(db.values()))
        words.append(next_word)

    def generate_markov_text(self, num_words, seed=None):
        if seed:
            phrase = tuple(w.lower().strip(PUNCTUATION) for w in seed.split())
            if phrase in self.database:
                words = list(phrase)
            else:
                seed_word = random.choice(seed.split())
                matches = self.key_list.get(seed_word.lower().strip(PUNCTUATION))
                matches = [m for m in matches if STOP_TOKEN not in m]
                if matches:
                    words = list(random.choice(matches))
                else:
                    raise ValueError("Not found.")
        else:
            words = list(random.choice(self.database.keys()))

        words = list(reversed(words))
        while not STOP_TOKEN in words:
            self.add_word(words, db=self.reversed)
        words = [w for w in reversed(words) if w != STOP_TOKEN]

        for i in range(num_words):
            self.add_word(words)
        while words[-1] != STOP_TOKEN:
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
    print(text)

if __name__ == '__main__':
    main()
