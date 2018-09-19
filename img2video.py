
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
consumer_key = "Enter Consumer Key here"
consumer_secret = "Enter Consumer Secret here"
access_key = "Enter Access Key here"
access_secret = "Enter Acess Secret here"



def create_dir(dir_name):
	#Make an Image directory to save images from tweets
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)
	else:
		#If directory exists, clear its contents to save the downloaded images
		folder = dir_name
		for the_file in os.listdir(folder):
			file_path = os.path.join(folder, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception as e:
				print(e)

def get_image_url(tweets):
	#Get images from the tweets
	media_files = set()
	for status in tweets:
		media = status.entities.get('media', [])
		if(len(media) > 0):
			media_files.add(media[0]['media_url'])
	return media_files

def download_images(media_files):
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

def convert_images_to_video(screen_name):
	os.system("ffmpeg -r 1/2 -i images/images%d.jpg -vcodec mpeg4 -y "+screen_name+".mp4")

def store_video_gs(screen_name):
	video_name = screen_name+".mp4"
	from google.cloud import storage
	# Instantiates a client
	storage_client = storage.Client()
	bucket = storage_client.get_bucket("twittervideobucket")
	blob = bucket.blob(video_name)
	blob.upload_from_filename(video_name)
	print('File {} uploaded to {}.'.format(
	video_name,
	video_name))

def process_video_google_vi(screen_name):
	video_name = screen_name+".mp4"
	from google.cloud import videointelligence
	video_client = videointelligence.VideoIntelligenceServiceClient()
	features = [videointelligence.enums.Feature.LABEL_DETECTION]
	operation = video_client.annotate_video('gs://twittervideobucket/'+video_name, features=features)
	print('\nProcessing video for label annotations:')
	result = operation.result(timeout=90)
	print('\nFinished processing.')
	# first result is retrieved because a single video was processed
	segment_labels = result.annotation_results[0].segment_label_annotations
	for i, segment_label in enumerate(segment_labels):
		print('Video label description: {}'.format(segment_label.entity.description))
		for category_entity in segment_label.category_entities:
			print('\tLabel category description: {}'.format(category_entity.description))

		for i, segment in enumerate(segment_label.segments):
			start_time = (segment.segment.start_time_offset.seconds + segment.segment.start_time_offset.nanos / 1e9)
			end_time = (segment.segment.end_time_offset.seconds +
			segment.segment.end_time_offset.nanos / 1e9)
			positions = '{}s to {}s'.format(start_time, end_time)
			confidence = segment.confidence
			print('\tSegment {}: {}'.format(i, positions))
			print('\tConfidence: {}'.format(confidence))
		print('\n')

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
	

	create_dir("images")
	media_files = get_image_url(tweets)
	download_images(media_files)
	convert_images_to_video(screen_name)
	store_video_gs(screen_name)
	process_video_google_vi(screen_name)

if __name__ == '__main__':
    #pass in the username of the account you want to download


    get_all_tweets("NatGeoPhotos")
