# This reddit bot fetches for comments in /r/test and checks if they have !true
# in them, if so, it sends a random joke from ICNDb.com as a reply to those
# comments

import praw
import time
import os
import requests


REPLY_MESSAGE_ENDING = '\n\nThis joke is from [ICNDb.com](http://icndb.com).'


def authenticate():
	print("Authenticating...")
	reddit = praw.Reddit(
		'jokebot',
		user_agent="glebkrep's joke commment responder")
	print("Authenticated as {}".format(reddit.user.me()))
	return(reddit)


def run_bot(reddit, comments_replied_to):
	print("Obtaining 25 comments...")

	for comment in reddit.subreddit('test').comments(limit=25):
		if "!true" in comment.body \
			and comment.id not in comments_replied_to:  # \
			# reply only to comments I didnt make
			# and not comment.author ==reddit.user.me():
			print('String with keyword found in comment: ' + comment.id)

			# compyling a comment and sending it
			comment_reply = "You requested a joke! Here it is:\n\n"
			joke = requests.get(
				"http://api.icndb.com/jokes/random").json()['value']['joke']
			comment_reply += ">" + joke + REPLY_MESSAGE_ENDING
			comment.reply(comment_reply)

			print('Replied to comment')
			# adding comment id to the cache so we won't reply to it again
			comments_replied_to.append(comment.id)
			with open('comments_replied_to.txt', 'a') as f:
				f.write(comment.id + '\n')
	# sleep for 10 seconds
	print(comments_replied_to)
	print('sleeping for 10 secs')
	time.sleep(10)


def get_saved_comments():
	if not os.path.isfile('comments_replied_to.txt'):
		comments_replied_to = []
	else:
		with open('comments_replied_to.txt', 'r') as f:
			comments_replied_to = f.read()
			comments_replied_to = comments_replied_to.split('\n')

		return(comments_replied_to)


def main():
	reddit = authenticate()
	# getting comments from cached file
	comments_replied_to = get_saved_comments()

	while True:
		run_bot(reddit, comments_replied_to)


# makes script run if we opened the file directrly (not imported)
if __name__ == '__main__':
	main()
