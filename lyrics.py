import os
import telebot
import requests
from dotenv import load_dotenv
from telebot import types

# getting token and headers from env file
load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
HEADERS = {
		'X-RapidAPI-Key': os.environ.get('KEY'),
		'X-RapidAPI-Host': os.environ.get('HOST')
	}
# all the search music function
# looking for artist - searching for id, getting description from this id and cover photo
def find_artist(artist):
	url = 'https://genius-song-lyrics1.p.rapidapi.com/search/multi/'
	querystring = {'q':artist}
	headers = HEADERS
	response = requests.request('GET', url, headers=headers, params=querystring)
	answer= response.json()['sections'][3]['hits']
	if not answer:
		raise Exception
	answer = answer[0]['result']
	artist_id = answer['id']
	cover_photo = answer['image_url']
	title = answer['name']
	description = artist_details(artist_id)
	return title, description, cover_photo
# looking for song id
def find_song(song):
	url = 'https://genius-song-lyrics1.p.rapidapi.com/search/'
	querystring = {'q':song}
	headers = HEADERS
	response = requests.request('GET', url, headers=headers, params=querystring)
	response = response.json()['hits'][0]['result']
	return response['id'], response['full_title']
# artist description just because
def artist_details(id):
	url = 'https://genius-song-lyrics1.p.rapidapi.com/artist/details/'
	querystring = {'id':id, 'text_format':'plain'}
	headers = HEADERS
	response = requests.request('GET', url, headers=headers, params=querystring)
	return response.json()['artist']['description']['plain']
# searching for lyrics
def song_lyrics(song):
	url = 'https://genius-song-lyrics1.p.rapidapi.com/song/lyrics/'
	song_id, title = find_song(song)
	querystring = {'id':song_id, 'text_format':'plain'}
	headers = HEADERS
	response = requests.request('GET', url, headers=headers, params=querystring)
	return title, response.json()['lyrics']['lyrics']['body']['plain']

# ------------------------BOT -------------------------
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['artist'])
def get_artist(message):
	msg = bot.send_message(message.chat.id, text='Please type the artist name')
	bot.register_next_step_handler(msg, artist_desc)

# looking for artist and if not found send sad photo of the cat 
def artist_desc(message):
	try:
		artist, desc, photo = find_artist(message.text)
		bot.send_message(message.chat.id, text= '<b> 💽 '+ artist + ' </>', parse_mode='html')
		bot.send_message(message.chat.id, text= '<i> '+ desc + ' </>', parse_mode='html')
		bot.send_photo(message.chat.id, photo)
	except Exception as e:
		bot.send_message(message.chat.id, 'Can\'t find this artis. Can you try again?')	
		bot.send_photo(message.chat.id,'https://i.pinimg.com/474x/5c/09/ab/5c09ab5bc07ef08b98e402572939db4d.jpg')

# searching for song after command
@bot.message_handler(commands=['song'])
def lyrics(message):
	msg = bot.send_message(message.chat.id, text = '🎼 type song name (use artist name for better result)')
	bot.register_next_step_handler(msg, get_text)
# just title and lyrics (because if artist is not specified are similar can give wrong results)
def get_text(message):
	try:
		title, lyrics = song_lyrics(message.text)
		bot.send_message(message.chat.id, text= '<b> 🎤 '+ title + ' </>', parse_mode='html')
		bot.send_message(message.chat.id, text= '<i> '+ lyrics + ' </>', parse_mode='html')
	except Exception as e:
		bot.send_message(message.chat.id, 'Can\'t find this song. Can you try again?')	
		bot.send_photo(message.chat.id,'https://i.pinimg.com/474x/5c/09/ab/5c09ab5bc07ef08b98e402572939db4d.jpg')

# Enable saving next step handlers to file './.handlers-saves/step.save'.
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default './.handlers-saves/step.save')
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()	
bot.infinity_polling()
