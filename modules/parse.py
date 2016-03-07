import sys
import re
from config import load_config

TKN_WORD = 0
TKN_OPTION = 1
TKN_EOF = 2

help = None
tokens = []
token = None

class Search:
	def __init__(self, opts, root, words):
		self.opts = opts
		self.root = root
		self.words = words

class Subcommand:
	def __init__(self, cmd, args):
		self.cmd = cmd
		self.args = args

def lexical():
	global tokens

	args = sys.argv[1:]

	for arg in args:
		if re.match('^-((-[a-z]+)+|[a-z]+)$', arg): # accepting just short options for the moment
			tokens.append({'value': arg, 'type': TKN_OPTION})
		elif re.match('^[\w/. :\\\\]+$', arg): 
			tokens.append({'value': arg, 'type': TKN_WORD})
		else:
			print 'Unreconized token in: %s' % arg 
			sys.exit()

	tokens.append({'value': '', 'type': TKN_EOF})

def nextToken():
	global tokens, token
	
	if (len(tokens) > 0):
		token = tokens[0]
		tokens = tokens[1:]

def checkToken(token_type):
	token_value = token['value']

	if (token['type'] == token_type):
		nextToken()
		return token_value
	elif (token['type'] == TKN_EOF):
		print 'Was expecting more arguments'
	else:
		print 'Unexpected argument:', token_value

	print help
	sys.exit()
	

def parse(doc):
	global help

	help = doc

	result = None

	lexical()

	nextToken()

	if token['value'] in ['set', 'unset', 'open', 'echo']:
		command = token['value']
		args = {}
		nextToken()

		if command == 'set':
			args['var_name'] = checkToken(TKN_WORD)
			args['path'] = checkToken(TKN_WORD)

		elif command == 'unset':
			args['var_name'] = checkToken(TKN_WORD)
			
		elif command == 'open':
			args['var_name'] = checkToken(TKN_WORD)

		elif command == 'echo':
			if (token['type'] == TKN_WORD): # optional argument
				args['var_name'] = token['value']
				nextToken()

		result = Subcommand(command, args)
	else:
		return search()

	checkToken(TKN_EOF)

	return result


def search():
	options = []
	search_obj = None
	words = []

	options = options_list()

	root = root_word()

	words.append(checkToken(TKN_WORD))

	words.extend(list_of_words())

	search_obj = Search(options, root, words)

	return search_obj

def root_word():
	path = None
	config = load_config()

	if token['value'] in config['paths']:
		path = token['value']
		nextToken()

	return path

def options_list():
	options = []

	if (token['type'] == TKN_OPTION):
		options.append(token['value'])
		nextToken()
		options.extend(options_list())

	return options

def list_of_words():
	words = []

	if (token['type'] == TKN_WORD):
		words.append(token['value'])
		nextToken()
		words.extend(list_of_words())

	return words