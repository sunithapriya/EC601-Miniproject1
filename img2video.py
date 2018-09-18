
# encoding: utf-8
#Author - Sunitha Priyadarshini Sampath

import tweepy
from tweepy import OAuthHandler
import os
import wget
import ffmpeg
import sys

#testbranch1

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
	#last_id = tweets[-1].id
 
	# while (True):
	# 	get_tweets = api.user_timeline(screen_name = screen_name,count=200,include_rts=False,exclude_replies=True,max_id=last_id-1)
	# 	# There are no more get_tweets
	# 	if (len(get_tweets) == 0):
	# 		break
	# 	else:
	# 		last_id = get_tweets[-1].id-1
	# 		tweets = tweets + get_tweets  
	media_files = set()
	for status in tweets:
		media = status.entities.get('media', [])
		if(len(media) > 0):
			media_files.add(media[0]['media_url'])
	#print(media_files)

	if not os.path.exists("images"):
		os.makedirs("images")
	else:
		folder = 'images'
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception as e:
				print(e)
	num = 1
	

	for media_file in media_files:
		numstr = str(num)
		file_name = os.path.split(media_file)[1]
		ext_name = file_name.split(".")
		file_name = "images"+numstr+"."+ext_name[1]
		output_folder = "images"
		if not os.path.exists(os.path.join(output_folder, file_name)):
			wget.download(media_file +":orig", out=output_folder+'/'+file_name)
			num+= 1

	os.system("ffmpeg -r 1 -i images/images%d.jpg -vcodec mpeg4 -y movie.mp4")
	
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()
bucket = storage_client.get_bucket("twittervideobucket")
blobs = bucket.list_blobs()
# for blob in blobs:
# 	print("in blob\n")
# 	print(blob.name)
blob = bucket.blob('movie.mp4')

blob.upload_from_filename('movie.mp4')

print('File {} uploaded to {}.'.format(
	'movie.mp4',
	'movie.mp4'))

from google.cloud import videointelligence

video_client = videointelligence.VideoIntelligenceServiceClient()
features = [videointelligence.enums.Feature.LABEL_DETECTION]
operation = video_client.annotate_video(
	'gs://twittervideobucket/movie.mp4', features=features)
print('\nProcessing video for label annotations:')

result = operation.result(timeout=90)
print('\nFinished processing.')

# first result is retrieved because a single video was processed
segment_labels = result.annotation_results[0].segment_label_annotations
for i, segment_label in enumerate(segment_labels):
	print('Video label description: {}'.format(
		segment_label.entity.description))
	for category_entity in segment_label.category_entities:
		print('\tLabel category description: {}'.format(
			category_entity.description))

	for i, segment in enumerate(segment_label.segments):
		start_time = (segment.segment.start_time_offset.seconds +
			segment.segment.start_time_offset.nanos / 1e9)
		end_time = (segment.segment.end_time_offset.seconds +
			segment.segment.end_time_offset.nanos / 1e9)
		positions = '{}s to {}s'.format(start_time, end_time)
		confidence = segment.confidence
		print('\tSegment {}: {}'.format(i, positions))
		print('\tConfidence: {}'.format(confidence))
	print('\n')

if __name__ == '__main__':
    #pass in the username of the account you want to download
    get_all_tweets("instagram")
