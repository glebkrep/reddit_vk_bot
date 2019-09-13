import time
import vk_api
import sys



# authenticating as vk.com/hhhinternational
def auth():
	print('authenticating...')
	vk = vk_api.VkApi(token = '???')
	vk.auth()
	print('authentication successful')
	return vk


	# sends a message to a user with 'user_id'


# sending a message to a user with user_id
def write_msg(vk, user_id, message):
	vk.method('messages.send',{'user_id':user_id,'message':message})
	print('"',message,'" sent to id/',user_id)


# returns all the inbox messages
def get_msgs(vk):
	values = {'out':0,'count':100,'time_offset':60}
	return vk.method('messages.get',values),values


# answers to all the messages it has recieved in real time
def answer_to_msgs(vk,message):
	print('starting to answer')

	while True:
		inbox = vk.method('messages.get',values)
		if inbox['items']:
			values['last_message_id'] = inbox['items'][0]['id']
		for item in inbox['items']:
			write_msg(vk,item[u'user_id'],message)
		time.sleep(2)


# answers to all the messages it has recieved
def answer_to_msgs_once(vk,message,values):
	print('starting to answer')


	inbox = vk.method('messages.get',values)
	if inbox['items']:
		values['last_message_id'] = inbox['items'][0]['id']
	for item in inbox['items']:
		write_msg(vk,item[u'user_id'],message)
	time.sleep(2)


def return_list_of_messages(vk,values):
	dic_r={}
	inbox = vk.method('messages.get',values)
	if inbox['items']:
		values['last_message_id'] = inbox['items'][0]['id']
	for item in inbox['items']:
		#print(item)
		if not item['user_id'] in dic_r:
			dic_r[item['user_id']] = []
		dic_r[item['user_id']].append(item['body'])
	
	return dic_r

#def respond_to_commands(vk,values,msg):
#	dic_r=return_list_of_messages(vk,values)
#	for user in dic_r:
#		print(dic_r[user])
#		if '!new' in dic_r[user]:
#			write_msg(vk,user,msg)


if __name__ == "__main__":

	#try:
		values = {'out':0,'count':100,'time_offset':60}

		file_name, function_name, user_id, message = sys.argv
		vk = auth()
		if function_name == 'write_msg':
			write_msg(vk,user_id,message)

		elif function_name == 'answer_to_all':
			answer_to_msgs(vk,message)

		elif function_name == 'list':
			return_list_of_messages(vk,values)
		elif function_name == 'respond_to':
			respond_to_commands(vk,values,'here you go')
		else:
			print('this function does not exist...')

#	except NameError:
#		print('USAGE: py _file_name _function_name(write_msg/answer_to_all) _user_id, _message')
#	except ValueError:
#		print('USAGE: py _file_name _function_name(write_msg/answer_to_all) _user_id, _message')


	
