import random, sys
from argparse import ArgumentParser

# after num_words, we keep going until we reach the end of a sentence
STOP_CHARS = ['.', '!', '?']

class markovgen(object):
	def __init__(self, filename, chain_len):
		self.chain_len = chain_len
		words = open(filename).read().split()
		self.database = self.build_database(words, self.chain_len)

	def build_database(self, words, chain_len):
		database = {}
		for chain in [words[i:i+(chain_len)] for i in range(len(words) - (chain_len - 1))]:
			key = tuple(chain[:-1])
			if key not in database:
				database[key] = []
			database[key].append(chain[-1])
		return database

	def add_word(self, words):
			words.append(random.choice(self.database[tuple(words[-(self.chain_len-1):])]))

	def generate_markov_text(self, num_words, seed):
		if seed:
			matches = filter(lambda key: seed.lower() in key or seed.capitalize() in key, self.database.keys())
			if len(matches) == 0:
				raise Exception("Seed not present in corpus")
			words = list(random.choice(matches))
		else:
			words = list(random.choice(self.database.keys()))
		for i in range(num_words):
			self.add_word(words)
		while not any([c in words[-1] for c in STOP_CHARS]):
			self.add_word(words)
		return ' '.join(words)

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
