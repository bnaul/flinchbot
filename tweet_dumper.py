import tweepy
import re

# Twitter API credentials
access_key = '221999764-G5wG7Y1i9vk08y5luaWvZBqkiyg79SuxrscGNqxg'
access_secret = 'PalNiTipirGk2gMiPWFhEOgyGogGMREBzwyvWwMxBYNbM'
consumer_key = 'XrdG4LqVexck4FqOdWa0YAUNY'
consumer_secret = 'X9CJobpSi8EEJhGqhnd5uEof3eHcaYSwjEiGEXX6kjkeVVpvky'


def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
#        print("getting tweets before %s" % (oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

#        print("...%s tweets downloaded so far" % (len(alltweets)))

    #transform the tweepy tweets into a 2D array that will populate the csv
    texts = [tweet.text for tweet in alltweets]# if 'Android' in tweet.source]
    texts = [re.sub('http://.*', '', t) for t in texts]
    texts = [re.sub('https://.*', '', t) for t in texts]
    texts = [t for t in texts if ' | ' not in t]
    texts = [t for t in texts if 'RT @' not in t]
    for t in texts:
        print(t)


if __name__ == '__main__':
    #pass in the username of the account you want to download
    get_all_tweets("realDonaldTrump")
