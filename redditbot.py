# This reddit bot fetches recent posts in /r/test and checks if they have !true
# in them, if so, it sends a random joke from ICNDb.com as a reply to those
# comments

import praw
import time
import os
import requests
import sys
import vk_mine

NEW_POSTS_AMOUNT = 100
# score to get to worthy_posts
THRESHOLD_FOR_WORTHY = 20
# seconds
SLEEP_TIME = 30

# hours
MAXIMUM_TIME_STORED = 12

SUBREDDIT = 'hiphopheads'

CRITERIA = "[fresh"

def authenticate():
	print("Authenticating...")
	reddit = praw.Reddit(
		'hhh',
		user_agent="glebkrep's /r/hhh [fresh] posts collector")
	print("Authenticated as {}".format(reddit.user.me()))
	return(reddit)

# list of all the fresh posts     { 'id':[title, link, score, time_created], [...], [...], [...] }
temp_posts = {}


# list of temp_posts that are over 50 upvotes
worthy_posts = {}

# all the posts that were considered ( temp_posts -> old_posts )
# 										if >= 50 upvotes -> worthy_posts
old_posts = []


people_db={}

# fixed
def check_for_new_fresh(reddit, old_posts, temp_posts):

	print("Obtaining ",NEW_POSTS_AMOUNT, " NEW posts...")
	subreddit = reddit.subreddit(SUBREDDIT)
	for submission in subreddit.new(limit=NEW_POSTS_AMOUNT):
		print('Checking post ',submission.id,'...')
		time_created = submission.created_utc

		if CRITERIA in submission.title.lower() \
			and submission.id not in old_posts:

			print('Found new post: ' + submission.id)
			# adding post id to the cache so we won't add it again
			ID = submission.id
			title = submission.title
			link = submission.url
			score = submission.score
			# time_created = submission.created_utc
			temp_posts[ID] = [title, link, score, time_created]

			print('POST_INFO... ',ID,': ',temp_posts[ID])

			title_new=decode(title)

			cached_submission = ID + ';' + title_new + ';' + link + ';' + str(score) + ';' + str(time_created)
						
			with open('temp_posts.txt', 'a') as f:
				f.write(cached_submission + '\n')
			with open('old_posts.txt','a') as f:
				f.write(ID + '\n')

			print('cached.')

	print('checked for {}'.format(NEW_POSTS_AMOUNT),' NEW posts.')
# Fixed
def check_for_hot_fresh(reddit,old_posts,temp_posts):
	print("Obtaining ",NEW_POSTS_AMOUNT, " NEW posts...")
	subreddit = reddit.subreddit('hiphopheads')
	for submission in subreddit.hot(limit=NEW_POSTS_AMOUNT):
		print('Checking post ',submission.id,'...')
		if "[fresh" in submission.title.lower() \
			and submission.id not in old_posts:

			print('Found hot post: ' + submission.id)
			# adding post id to the cache so we won't add it again
			ID = submission.id
			title = submission.title
			link = submission.url
			score = submission.score
			time_created = submission.created_utc
			temp_posts[ID] = [title, link, score, time_created]

			title_new=decode(title)

			print('POST_INFO... ',ID,': ',temp_posts[ID])
			cached_submission = ID + ';' + title_new + ';' + link + ';' + str(score) + ';' + str(time_created)
						
			with open('temp_posts.txt', 'a') as f:
				f.write(cached_submission + '\n')
			with open('old_posts.txt','a') as f:
				f.write(ID + '\n')

			print('cached.')
	print('checked for {}'.format(NEW_POSTS_AMOUNT),' HOT posts.')	
# FIXED
def uncache(filename, bool_dictionary):
	print('UNCACHING ',filename)
	if not os.path.isfile(filename):
		listing = {}
	else:
		
		with open(filename,'r') as f:
			filedata = f.read()
			filedata = filedata.split('\n')
		if bool_dictionary:
			listing = {}
			for item in filedata:
				if item!="":
					data = item.split(';')
					#print(data)
					ID = data[0]
					title = data[1]
					link = data[2]
					score = float(data[3])
					time_created = float(data[4])

					listing[ID] = [title, link, score, time_created]
		else:
			listing = []
			for item in filedata:
				if item!="":
					listing.append(item)
	#print('extracted::: ', listing, ' ::: from ',filename)
	print('extracted')
	return(listing) 

# FIXED
def temp_post_resort(reddit, temp_posts, old_posts, worthy_posts):
	#iteration is used to track the lines that should be deleted
	print('sorting initialized')
	iteration=0
	to_delete=[]
	for item in temp_posts:
		submission = reddit.submission(id=item)
		if submission.score>=THRESHOLD_FOR_WORTHY:
			print('.')
			print('WORTHY: ',temp_posts[item])
			to_delete.append(iteration)
		iteration+=1	

	# deleting all not needed lines from temp_posts.txt
	f = open('temp_posts.txt','r')
	# lines - all the data in temp_posts.txt
	lines=f.readlines()
	f.close()
	f=open('temp_posts.txt','w')
	iteration=0
	for line in lines:
		if not iteration in to_delete:
			#print(line,' is back to temp')
			f.write(line)
		else:
			with open('worthy_posts.txt', 'a') as wp:
				wp.write(line)
				print(line,' deleted from temp, moved to worthy')
		iteration+=1
	f.close()
	print('sorting is over')

# FIXED: change={'id':delete,'id':1} where 1 = integer to which i should change score
#
def update_scores_for_temp(reddit, temp_posts):
	change = {}
	iteration = 0
	curr_time = time.time()
	#open('temp_posts.txt', 'w').close()
	for item in temp_posts:

		submission = reddit.submission(id=item)


		ID = item
		title = temp_posts[ID][0]
		link = temp_posts[ID][1]
		score = submission.score
		time_created = temp_posts[ID][3]

		score_before=temp_posts[ID][2]

		# updated the temp_posts
		temp_posts[ID] = [title, link, score, time_created]

		
		if (curr_time-int(time_created))//3600>=MAXIMUM_TIME_STORED and score< THRESHOLD_FOR_WORTHY:
			print("Deleted from temp: ",temp_posts[ID])
			change[iteration] = 'delete'
		else:			
			if score_before!=score:
				print('FROM::::',[title,link,score_before,time_created])
				print('TO  ::::',temp_posts[item])
				cached_submission = ID + ';' + title + ';' + link + ';' + str(score) + ';' + str(time_created)	
				change[iteration] = cached_submission
			#with open('temp_posts.txt', 'a') as f:
			#		f.write(cached_submission + '\n')
		iteration += 1
		print('next')
		
	f = open('temp_posts.txt','r')
	# lines - all the data in temp_posts.txt
	lines=f.readlines()
	f.close()
	f=open('temp_posts.txt','w')
	iteration=0
	for line in lines:
		if not iteration in change:
			f.write(line)
		elif change[iteration] != 'delete':
			f.write(change[iteration]+'\n')
			
		iteration+=1
	f.close()


def update_scores_for_worthy(reddit, worthy_posts):
	change = {}
	iteration = 0
	curr_time = time.time()
	#open('worthy_posts.txt', 'w').close()
	for item in worthy_posts:

		submission = reddit.submission(id=item)


		ID = item
		title = worthy_posts[ID][0]
		link = worthy_posts[ID][1]
		score = submission.score
		time_created = worthy_posts[ID][3]

		score_before=worthy_posts[ID][2]

		# updated the worthy_posts
		worthy_posts[ID] = [title, link, score, time_created]

		
			
		if score_before!=score:
			print('FROM::::',[title,link,score_before,time_created])
			print('TO  ::::',worthy_posts[item])
			cached_submission = ID + ';' + title + ';' + link + ';' + str(score) + ';' + str(time_created)	
			change[iteration] = cached_submission
			#with open('worthy_posts.txt', 'a') as f:
			#		f.write(cached_submission + '\n')
		iteration += 1
		print('next')
		
	f = open('worthy_posts.txt','r')
	# lines - all the data in worthy_posts.txt
	lines=f.readlines()
	f.close()
	f=open('worthy_posts.txt','w')
	iteration=0
	for line in lines:
		if not iteration in change:
			f.write(line)
		elif change[iteration] != 'delete':
			f.write(change[iteration]+'\n')
			
		iteration+=1
	f.close()


def send_worthy(vk,values,worthy_posts,user_id,people_db, final_line_n):
	# BUG MIGHT HAPPEN
	user_id = str(user_id)
	print('sending to :::',user_id,':::')
	change = {}
	composed_message=time.strftime('%a, %d %b %Y %H:%M:%S in omsk', time.localtime())+'\n'+'\n'	
	if not user_id in people_db:
			people_db[user_id] = []

	iteration=0
	for post in worthy_posts:
		
		if not post in people_db[user_id]:
			people_db[user_id].append(post)
			iteration += 1

			composed_message+=str(worthy_posts[post][0])+' '+str(worthy_posts[post][1]+'\n'+'\n')
			if len(composed_message)>3500:
				vk_mine.write_msg(vk, user_id, composed_message)
				composed_message=''
				time.sleep(1)

	if iteration>0:
		composed_message+= "=======THAT'S ALL, FOLKS!======="+'\n'
	else:
		composed_message = 'Nothing new. BabyRage'	
	vk_mine.write_msg(vk, user_id, composed_message)

	cached_submission = str(user_id)
	for i in people_db[user_id]:
		if i != user_id:
			cached_submission += ';'+i


	f = open('people_db.txt','r')
	# lines - all the data in temp_posts.txt
	lines=f.readlines()
	f.close()
	f=open('people_db.txt','w')
	j=0
	for line in lines:
		print(line)
		if j != int(final_line_n) or iteration==0:
			print('not_changing')
			f.write(line)
		else:
			print('changing')

			f.write(cached_submission + '\n')
			
		j+=1
	if iteration>0 and int(final_line_n) == -1:
		f.write(cached_submission + '\n')
		print('caching new')

			
	f.close()
	print('cached.')


def decode(text):
	text_new=''
	for letter in text:
		if not letter in "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890=+()[]-_":
			if letter == '$':
				text_new+="S"
			else:
				text_new+=' '
		else:
			text_new+=letter	
	return text_new

# USAGE: py redditbot.py FUNCTION_NAME(all/new/resort/update)
def main(function_name=sys.argv[1]):
	reddit = authenticate()

	values = {'out':0,'count':100,'time_offset':60}
	vk = vk_mine.auth()

	#user_id = str(82251556)

	# getting data from cached file

	# temp_posts = uncache('temp_posts.txt')
	# worthy_posts = uncache('worthy_posts.txt')
	# old_posts = uncache('old_posts.txt')
	print('____________________START____________________')

	if function_name == 'new':
		print('EXECUTING: ',function_name)


		temp_posts = uncache('temp_posts.txt', True)
		old_posts = uncache('old_posts.txt', False)

		check_for_new_fresh(reddit,old_posts, temp_posts)

	elif function_name == "sort":
		print('EXECUTING: ',function_name)

		temp_posts = uncache('temp_posts.txt', True)
		worthy_posts = {}
		old_posts = uncache('old_posts.txt', False)

		temp_post_resort(reddit, temp_posts, old_posts, worthy_posts)

	elif function_name == 'update':
		print('EXECUTING: ',function_name)

		temp_posts = uncache('temp_posts.txt', True)

		update_scores_for_temp(reddit, temp_posts)	

	elif function_name == 'hot':
		print('EXECUTING: ',function_name)

		temp_posts = uncache('temp_posts.txt', True)
		old_posts = uncache('old_posts.txt', False)

		check_for_hot_fresh(reddit,old_posts,temp_posts)	

	# FOR NOW IS JUST FOR MANUAL USAGE
	elif function_name == 'update_worthy':
		print('EXECUTING: ',function_name)
		worthy_posts = uncache("worthy_posts.txt", True)

		update_scores_for_worthy(reddit, worthy_posts)


	elif function_name == 'send_worthy':
		print('EXECUTING: ',function_name)

		
		worthy_posts = uncache('worthy_posts.txt',True)


		with open('people_db.txt','r') as f:
			filedata = f.read()
			filedata = filedata.split('\n')

		for item in filedata:
			item=item.split(';')
			vk_id=item[0]
			people_db[vk_id]=[]
			for word in item:
				people_db[vk_id].append(word)

		send_worthy(vk,values,worthy_posts,user_id,people_db)


	elif function_name == 'all':
		i=0
		while True:
			#try:
				print('cycle: ',i)
				if i == 30 or i == 1:
					print("UPDATE_TIME!")
					temp_posts = uncache('temp_posts.txt', True)
					worthy_posts = {}
					old_posts = uncache('old_posts.txt', False)

					update_scores_for_temp(reddit, temp_posts)

					temp_posts = uncache('temp_posts.txt', True)
					worthy_posts = {}
					old_posts = uncache('old_posts.txt', False)

					check_for_hot_fresh(reddit,old_posts,temp_posts)

					temp_posts = uncache('temp_posts.txt', True)
					worthy_posts = {}
					old_posts = uncache('old_posts.txt', False)

					check_for_new_fresh(reddit,old_posts, temp_posts)

					temp_posts = uncache('temp_posts.txt', True)
					worthy_posts = {}
					old_posts = uncache('old_posts.txt', False)

					temp_post_resort(reddit, temp_posts, old_posts, worthy_posts)
					if i!=1:
						i = 0
								

				#return list of messages
				#check if !new in any of them
				#send worthy to them



				line_n=0
				final_line_n=-1

				dic_r = vk_mine.return_list_of_messages(vk,values)
				for user in dic_r:
					print(user,' ',dic_r[user])
					if '!new' in dic_r[user]:
						with open('people_db.txt','r') as f:
							filedata = f.read()
							filedata = filedata.split('\n')
						people_db={}
						for line in filedata:

							if line!='':
								line=line.split(';')
								vk_id=line[0]
								people_db[vk_id]=[]
								for word in line:
									people_db[vk_id].append(word)
								if str(vk_id) == str(user):
									final_line_n = line_n
								line_n += 1
						worthy_posts = uncache('worthy_posts.txt',True)
						print(final_line_n)
						send_worthy(vk,values,worthy_posts,user,people_db,final_line_n)




			#except:
				#print('error occured, recovering___________________________________________')
				#continue
				i += 1
				print('====SLEEPING FOR',SLEEP_TIME,'====')
				time.sleep(SLEEP_TIME)

	else:
		print('NO FUNCTION SPECIFIED: USAGE: py redditbot.py FUNCTION_NAME(all/new/resort/update)')
		
	print('____________________FINISH____________________')

# makes script run if we opened the file directrly (not imported)
if __name__ == '__main__':
	main()
