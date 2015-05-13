import random
import tweepy
import textwrap
import logging
import re
from markovgen import markovgen

ACCESS_TOKEN = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN_SECRET = ''
USER_NAME = ''
DATA_FILE = ''

TWEETS_PER_DAY = 4
CHAIN_LEN = 3
MIN_WORDS = 4
MAX_WORDS = 20
MAX_TWEET_LENGTH = 140
MAX_THREAD_LEN = 8

STOP_CHARS = ['.', '!', '?'] # TODO guess these should be shared with markovgen

class flinchbot(object):
	def __init__(self, debug):
		self.debug = debug
		self.auth = tweepy.auth.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		self.auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
		self.api = tweepy.API(self.auth)
		self.last_id = None
		self.mentions = []
		self.markov = markovgen(DATA_FILE, CHAIN_LEN)

	def random_tweet(self):
		num_words = random.randint(MIN_WORDS, MAX_WORDS)
		resp = self.markov.generate_markov_text(num_words, None)
		return self.clean_text(resp)

	def clean_text(self, tweet):
		return tweet.replace('\n','')

	def truncate_tweet(self, tweet, nchar=MAX_TWEET_LENGTH):
		truncated = textwrap.wrap(tweet, nchar)[0]
		# looks better if we truncate at the end of a sentence
		stop_matches = list(re.finditer('['+''.join(STOP_CHARS)+']', truncated))
		if len(stop_matches) > 0:
			truncated = truncated[:stop_matches[-1].start()+1]
		return truncated

	def get_last_id(self):
		return self.api.user_timeline(screen_name=USER_NAME, count=1)[0].id

	def get_thread(self, status):
		if status.in_reply_to_status_id is None:
			return [status]
		else:
			parent = self.api.statuses_lookup((status.in_reply_to_status_id,))
			if len(parent) > 0:
				return [status] + self.get_thread(parent[0])
			else:
				return [status]

	def post(self):
		tweet = self.truncate_tweet(self.random_tweet())
		logging.debug("Posting: %s" % (tweet))
		if not self.debug:
			try:
				status = self.api.update_status(status=tweet)
				logging.debug("Posted %i" % status.id)
			except Exception, e:
				logging.debug("Failed to post status: " + str(e))
		else:
			print tweet

	def respond(self):
		try:
			self.last_id = self.get_last_id()
			self.mentions = self.api.mentions_timeline(since_id=self.last_id)
		except Exception, e:
			logging.debug("Failed to download mentions: " + str(e))
		threads = [self.get_thread(m) for m in self.mentions]
		child_map = {}
		for thread in threads:
			for i in range(len(thread)):
				for j in range(i):
					if thread[i].id not in child_map:
						child_map[thread[i].id] = set()
					child_map[thread[i].id].add(thread[j].id)
		for m, thread in zip(self.mentions, threads):
			if len(thread) > MAX_THREAD_LEN or m.id in child_map.keys():
				continue
			names = ['@' + m.user.screen_name] + filter(lambda x: x[0] == '@', m.text.split())
			if ('@' + USER_NAME) in names: # apparently mentions don't need to contain your name?
				names.remove('@' + USER_NAME)
			hashtags = filter(lambda word: word[0] == '#', m.text.split())
# if tweet is too long, we want to truncate the message, not the hashtags
			max_length = MAX_TWEET_LENGTH - (sum([len(x) for x in hashtags]) + len(hashtags))
			tweet = self.truncate_tweet(' '.join(names) + ' ' + self.random_tweet(), max_length) + ' ' + ' '.join(hashtags)
			if not self.debug:
				logging.debug("Responding to %i: %s" % (m.id, tweet))
				try:
					status = self.api.update_status(status=tweet, in_reply_to_status_id=m.id)
					logging.debug("Posted %i" % status.id)
				except Exception, e:
					logging.debug("Failed to post status: " + str(e))
			else:
				print "Responding to %i: %s" % (m.id, tweet)

if __name__ == '__main__':
	debug = False
	bot = flinchbot(debug)
	bot.respond()
# currently set up to run every minute, i.e. 24*60 times per day
	if random.random() < float(TWEETS_PER_DAY) / (24 * 60):
		bot.post()
