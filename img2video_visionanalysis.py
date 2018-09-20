
# encoding: utf-8
#Author - Sunitha Priyadarshini Sampath

import tweepy
from tweepy import OAuthHandler
import os
import wget
import ffmpeg
import sys
import io

#Twitter API credentials
consumer_key = "Enter Consumer Key"
consumer_secret = "Enter Consumer Secret"
access_key = "Enter Access Key"
access_secret = "Enter Access Secret"

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

def download_images(media_files,dir_name):
	#Download the images from the image url
	#Store the images with same name follwed by number to provide input for ffmpeg
	num = 1
	for media_file in media_files:
		numstr = str(num)
		file_name = os.path.split(media_file)[1]
		ext_name = file_name.split(".")
		file_name = "images"+numstr+"."+ext_name[1]
		output_folder = dir_name
		if not os.path.exists(os.path.join(output_folder, file_name)):
			wget.download(media_file +":orig", out=output_folder+'/'+file_name)
			num+= 1

def convert_images_to_video(screen_name):
	#Using ffmpeg to convert images to video.
	os.system("ffmpeg -loglevel panic -r 1/2 -i images/images%d.jpg -vcodec mpeg4 -y "+screen_name+".mp4")

def process_images_visionapi(dir_name):
	#Google APi for processing images
	from google.cloud import vision
	from google.cloud.vision import types
	# Instantiates a client
	client = vision.ImageAnnotatorClient()
	# The name of the image file to annotate
	images_to_analyse = os.listdir(dir_name)
	for l in images_to_analyse:
		file_name = os.path.join(os.path.dirname(__file__),'images/'+l)
		# Loads the image into memory
		with io.open(file_name, 'rb') as image_file:
			content = image_file.read()
		image = types.Image(content=content)
		# Performs label detection on the image file
		response = client.label_detection(image=image)
		labels = response.label_annotations
		print('Label for file_name:'+file_name)
		for label in labels:
			print(label.description)

def get_tweets(screen_name):
	#Authorise twitter
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
 
	api = tweepy.API(auth)

	#get tweets
	tweets = api.user_timeline(screen_name = screen_name,
                           count=200, include_rts=False,
                           exclude_replies=True)
	#twitter api allows a max of 200 tweets per user
	#the below code helps fetches 400 tweets 
	# 	count = 1
	# while (count == 2):
	# 	get_tweets = api.user_timeline(screen_name = screen_name,count=200,include_rts=False,exclude_replies=True,max_id=last_id-1)
	# 	count += 1
	# return tweets
	#twitter api allows a max of 200 tweets per user
	#the below code helps in fetching all tweets by changing the max_id after every fetch
	#The below code fetches all tweets
	#last_id = tweets[-1].id
	# while (True):
	# 	get_tweets = api.user_timeline(screen_name = screen_name,count=200,include_rts=False,exclude_replies=True,max_id=last_id-1)
	# 	# There are no more get_tweets
	# 	if (len(get_tweets) == 0):
	# 		break
	# 	else:
	# 		last_id = get_tweets[-1].id-1
	# 		tweets = tweets + get_tweets  
	return tweets

if __name__ == '__main__':
    #pass in the username of the account you want to download
    screen_name = "NatGeoPhotos"
    tweets = get_tweets(screen_name)
    #Enter directory name to store images
    dir_name = "images"
    create_dir(dir_name)
    media_files = get_image_url(tweets)
    download_images(media_files,dir_name)
    convert_images_to_video(screen_name)
    process_images_visionapi(dir_name)
