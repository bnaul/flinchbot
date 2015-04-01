from bs4 import BeautifulSoup
from argparse import ArgumentParser

# these are pretty arbitrary, but by default we use 3-word chains so anything less isn't useful
MIN_CHARS = 8
MIN_WORDS = 3

# strip everything after these strings: e.g. links, quoted text
STRINGS_TO_FILTER = ['http:', 'Sent at ']

def get_sender(message):
	return message.previous_sibling.span.text

def is_valid(message):
	return len(message) > MIN_CHARS and len(message.strip().split()) >= MIN_WORDS

def clean_message(message):
	message = message.strip()
	for ds in STRINGS_TO_FILTER:
		if ds in message:
			message = message[0:message.find(ds)].strip()
	if len(message) > 0 and message[-1].isalnum():
		message += '.'
	return message.encode('ascii', 'ignore')

if __name__ == '__main__':
	parser = ArgumentParser(prog='messageparse')
	parser.add_argument('-n', '--name', dest='name', required=True)
	parser.add_argument('-f', '--file', dest='filename', default='/dev/stdin')
	values = parser.parse_args()
	soup = BeautifulSoup(open(values.filename))
	p_tags = filter(lambda x: get_sender(x) == values.name, soup.find_all('p'))
	cleaned = [clean_message(p.text) for p in p_tags]
	valid = filter(is_valid, cleaned)
	for m in valid:
		print m
