import os
import tweepy

class TweetHandler():
    def __init__(self):
        try:
            consumer_key = os.environ['UNIVERSITY_EDITS_CONSUMER_KEY']
            consumer_secret = os.environ['UNIVERSITY_EDITS_CONSUMER_SECRET']
            access_key = os.environ['UNIVERSITY_EDITS_ACCESS_KEY']
            access_secret = os.environ['UNIVERSITY_EDITS_ACCESS_SECRET']
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_key, access_secret)
            self.api = tweepy.API(self.auth)
        except KeyError:
            print "One or more of the keys are missing from the environment"
            self.api = None

    def send_tweet(self, tweet):
        if self.api is not None:
            self.api.update_status(tweet)
            print "Sending tweet: %s" % tweet
        else:
            print "(NO API) %s" % tweet