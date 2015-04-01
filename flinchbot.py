import random
import tweepy
import textwrap
import logging
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
		return textwrap.wrap(tweet,nchar)[0]

	def get_last_id(self):
		return self.api.user_timeline(screen_name=USER_NAME, count=1)[0].id

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
		except:
			logging.debug("Failed to download mentions")
		for m in self.mentions:
			names = ['@' + m.user.screen_name] + filter(lambda x: x[0] == '@', m.text.split())
			names.remove('@' + USER_NAME)
			hashtags = filter(lambda word: word[0] == '#', m.text.split())
# if tweet is too long, we want to truncate the message, not the hashtags
			max_length = MAX_TWEET_LENGTH - (sum([len(x) for x in names+hashtags]) + len(names) + len(hashtags))
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
