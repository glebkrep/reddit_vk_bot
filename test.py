import praw
import time
import os
import requests




def authenticate():
	print("Authenticating...")
	reddit = praw.Reddit(
		'hhh',
		user_agent="glebkrep's /r/hhh [fresh] posts collector")
	print("Authenticated as {}".format(reddit.user.me()))
	return(reddit)

# list of all the fresh posts     { 'id':[name, link, upvotes, time], [...], [...], [...] }
temp_posts = {}

# list of temp_posts that are over 50 upvotes
worthy_posts = {}

# all the posts that were considered ( temp_posts -> old_posts )
# 										if >= 50 upvotes -> worthy_posts
old_posts = []

def check_for_new_fresh(reddit):
	print("Obtaining 100 posts...")
	subreddit = reddit.subreddit('hiphopheads')
	for submisssion in subreddit.new(limit=2):
		print('Checking post ',submisssion.id,'...')
		print(submisssion.id)
		print(submisssion.title)
		print(submisssion.url)
		print(submisssion.score)
		print(submisssion.created)

check_for_new_fresh(authenticate())