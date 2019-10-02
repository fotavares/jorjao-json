# -*- coding: utf-8 -*-
import time
import random
import telepot
import json
from telepot.loop import MessageLoop
import emoji
import sys
import logging
#import constants
import os
import psutil
import re
from pytz import timezone
from datetime import datetime

def find(regex, string):
	x = re.search(regex,string.decode('utf-8'))
	if x == None:
		return False
	else:
		return True

def handle(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	command = ''
	new_user = ''
	

	data = datetime.now(timezone('Brazil/East')).strftime('%d/%m/%Y %H:%M:%S')
	
	with open("jorjao.json", "r", encoding = "utf-8") as read_file:
			jsondata = json.load(read_file)

	#Privado
	if chat_type == 'private':
		#Padrão para admin
		if msg['from']['username'] == config["admin"]:
			if 'text' in msg:
				if msg['text'] == '/log':
					bot.sendDocument(chat_id,open(logFile,'rb'))
				if msg['text'] == '/restart':
					try:
						p = psutil.Process(os.getpid())
						for handler in p.open_files() + p.connections():
							os.close(handler.fd)
					except Exception as e:
						logging.error(e)
					python = sys.executable
					os.execl(python, python, *sys.argv)
			else:
				msgIdArquivo = ""
				if 'photo' in msg:
					msgIdArquivo = "photo - " + msg["photo"][0]["file_id"]
				if 'video' in msg:
					msgIdArquivo = "video - " + msg["video"]["file_id"]
				if 'document' in msg:
					if (msg["document"]["file_name"].endswith(".py") or 
					   msg["document"]["file_name"].endswith(".json") or
					   msg["document"]["file_name"].endswith(".db")):
						bot.download_file(msg["document"]["file_id"],msg["document"]["file_name"])
						bot.sendMessage(chat_id,"Arquivo salvo")
					else:
						msgIdArquivo = "docto - " + msg["document"]["file_id"]
				if 'voice' in msg:
					msgIdArquivo = "voice - " + msg["voice"]["file_id"]
				if 'sticker' in msg:
					msgIdArquivo = 'sticker - ' + msg["sticker"]["file_id"] + ' - ' + msg["sticker"]["emoji"]

				bot.sendMessage(chat_id,msgIdArquivo)
		
		#Configurado via json
		if 'text' in msg:
			command = msg['text'].lower()
			if '/relay' in command:
				bot.sendMessage(config["grupo"]["grupo"], '%s' % command[7:])
			if '/fala' in command:
				bot.sendMessage(config["grupo"]["grupo"], '%s' % command[6:])
			
			command = msg['text'].encode('utf-8').lower()
			for chave in jsondata['private']['actions']:
				if(find(r''+chave['word'],command)):
					chat_to_send = chat_id
					if(('chatid' in chave) and (chave['chatid'] != None)): 
							chat_to_send = int(chave['chatid'])
					if(chave['type'] == "text"):
						bot.sendMessage(chat_to_send,random.choice(chave['response']))
					elif(chave['type'] == "image"):
						bot.sendPhoto(chat_to_send, random.choice(chave['response']))
					elif(chave['type'] == "doc"):
						bot.sendDocument(chat_to_send, random.choice(chave['response']))


			logging.info('{} - {}({}): {}'.format(data,msg['from']['first_name'],msg['from']['username'], command))
			return

	#Usuario novo (grupo)
	if content_type == 'new_chat_member':
		for new_user in msg['new_chat_members']:
			if new_user['first_name'] != config["botname"]:
				if(jsondata["new_user"]["type"] == "text"):
					bot.sendMessage(chat_id, random.choice(jsondata["new_user"]["response"]) % new_user['first_name'])
				if(jsondata["new_user"]["type"] == "image"):
					bot.sendPhoto(chat_id, random.choice(jsondata["new_user"]["response"]))
				if(jsondata["new_user"]["type"] == "doc"):
					bot.sendDocument(chat_id, random.choice(jsondata["new_user"]["response"]))
				logging.info('{} entrou em {}'.format(new_user['first_name'], data))


	#Usuario Saiu (grupo)
	if content_type == 'left_chat_member':
		if(jsondata["new_user"]["type"] == "text"):
			bot.sendMessage(chat_id, random.choice(jsondata["left_user"]["response"]) % msg['left_chat_member']['first_name'])
		if(jsondata["new_user"]["type"] == "image"):
			bot.sendPhoto(chat_id, random.choice(jsondata["left_user"]["response"]))
		if(jsondata["new_user"]["type"] == "doc"):
			bot.sendDocument(chat_id, random.choice(jsondata["left_user"]["response"]))
		logging.info('{} saiu em {}'.format(msg['left_chat_member']['first_name'], data))

	#Mensagem no grupo	
	if content_type == 'text':
		command = msg['text'].encode('utf-8').lower()
		reply_id = msg['message_id']

		for chave in jsondata['public']['actions']:
			if(find(r''+chave['word'],command)):
				if(chave['type'] == "text"):
					bot.sendMessage(chat_id,random.choice(chave['response']) ,reply_to_message_id=reply_id)
				elif(chave['type'] == "emoji"):
					qty = 1
					if(('qty' in chave) and (chave['qty'] != None)): 
						qty = int(chave['qty'])
					bot.sendMessage(chat_id, emoji.emojize(random.choice(chave['response']) * qty,use_aliases=True),reply_to_message_id=reply_id)
				elif(chave['type'] == "image"):
					bot.sendPhoto(chat_id, random.choice(chave['response']),reply_to_message_id=reply_id)
				elif(chave['type'] == "doc"):
					bot.sendDocument(chat_id, random.choice(chave['response']),reply_to_message_id=reply_id)
				break

		if '/geralink' in msg['text']:
			bot.exportChatInviteLink(chat_id)
			bot.sendMessage(chat_id,"Novo link gerado! /link para receber")
		if '/link' in msg['text']:
			ch = bot.getChat(chat_id)
			bot.sendMessage(chat_id,ch['invite_link'])
			
logFile = os.path.basename(sys.argv[0].split('.')[0]) + '.log'

logging.basicConfig(filename=logFile,level=logging.INFO)

with open("config.json", "r", encoding = "utf-8") as read_file:
			config = json.load(read_file)

bot = telepot.Bot(config["token"])
updates = bot.getUpdates()

#Ignorar mensagens da fila quando reiniciar
if updates:
	last_update_id = updates[-1]['update_id']
	bot.getUpdates(offset=last_update_id+1)

MessageLoop(bot, handle).run_as_thread()
print ('I am listening ...')

while 1:
	time.sleep(10)
