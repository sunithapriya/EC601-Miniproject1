
# encoding: utf-8
#Author - Sunitha Priyadarshini Sampath

import tweepy
from tweepy import OAuthHandler
import os

#Twitter API credentials
consumer_key = "FVqVunV6OkKDtJ8HlSFvpBF3W"
consumer_secret = "nXCK8IgaWvbv3zJAxuQAw7lyooWzHZJCjrnFTvZFk7f2Ssf7vU"
access_key = "1040679655936798720-zE0fXGtzffQcazoHaZ3Mag5kSY6BAz"
access_secret = "omB1rnUwejSwORV4S4H4buZA2BXLV6437eYzQDn2lPyFg"

def get_all_tweets(screen_name):
	#Authorise twitter
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
 
	api = tweepy.API(auth)

	#get tweets
	tweets = api.user_timeline(screen_name = screen_name,
                           count=200, include_rts=False,
                           exclude_replies=True)
	#twitter api allows a max of 200 tweets per user
	#the below code helps in fetching all tweets by changing the max_id after every fetch
	last_id = tweets[-1].id
 
	# while (True):
	# 	get_tweets = api.user_timeline(screen_name = screen_name,count=200,include_rts=False,exclude_replies=True,max_id=last_id-1)
	# 	# There are no more tweets
	# 	if (len(get_tweets) == 0):
	# 		break
	# 	else:
	# 		last_id = get_tweets[-1].id-1
	# 		tweets = tweets + get_tweets  

	print(tweets)


if __name__ == '__main__':
    #pass in the username of the account you want to download
    get_all_tweets("NatGeo")