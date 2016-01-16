import os
import platform
import sys
import pickle

doc ='''
Instant File access

Usage:
	ifa [options] [<root>] <search_pattern>
	ifa unset <var_name>
	ifa set <var_name> <path>
	ifa open <var_name>
	ifa echo

Options:
	-d --directory  searchs a directory
'''

CONFIG_FILE_NAME = 'ifa.conf'
MEMORY_SIZE = 250

config_file_path = ''
list_results = False
memory = []
		
def search(search_root, search_pattern, search_for_directory):
	root = ''
	results = []
	compare.pattern = search_pattern.lower() # make case insensitive comparision

	config = load_config()
	
	if search_root is None:
		if 'default_root' in config['paths'] and config['paths']['default_root']:
			root = config['paths']['default_root']
		else:
			root = os.getcwd()
	else:
		if search_root in config['paths']:	
			# The given root is stored as path variable
			root = config['paths'][search_root]
		elif os.path.isdir(search_root):
			# The given root is a real path
			root = search_root
		else:
			print 'Error: <root> must be a path variable or a real path'

			sys.exit()

	# get all file names in the tree directory
	for dir_entries in os.walk(root):
		dir_path, directories, files = dir_entries

		if search_for_directory:
			entries = directories
		else:
			entries = files

		for entrie in entries:
			full_path = os.path.join(dir_path, entrie)

			compare.word = full_path.replace(root, '').lower() # use relative path for comparision
			
			initialize_memory()

			results.append({'path': full_path, 'factor': compare()})

	if len(results) > 0:
		results = sorted(results, reverse=True, key=lambda res: (res['factor'], len(res['path']) * -1))
		
		best_result = results[0]

		if list_results:
			count = 1
			for res in results:
				print '({})\n"{}" -> {}'.format(count, res['path'], res['factor'])
				
				if count % 5 == 0:
					raw_input(':')

				count += 1
		
		print 'Best match in: '
		print '"{}"'.format(best_result['path'])

		launch(best_result['path'])

def compare(i=0, j=0):
	global memory

	if i == len(compare.pattern) or j == len(compare.word):
		return 0

	# pos = compare.word.find(compare.pattern[i], j)

	# if (pos == -1):
	# 	return compare(i+1, j)
	# else:
	# 	return max(1 + compare(i+1, pos+1), compare(i+1, j))

	elif memory[i][j] != -1:
		return memory[i][j]
	else:
		pos = compare.word.find(compare.pattern[i], j)

		if (pos == -1):
			memory[i][j] = compare(i+1, j)
		else:
			memory[i][j] = max(1 + compare(i+1, pos+1), compare(i+1, j))

		return memory[i][j]

def launch(file_name):
	system = platform.system().lower()

	if 'windows' in system:
		os.system('start "" "' + file_name + '"')
	elif 'linux' in system:
		os.system('xdg-open "' + file_name + '"&')
	else:
		print 'Operative System not supported'

def load_config():
	config = {
		'paths': {'default_root': ''}
	}

	try:
		config_file = open(config_file_path, 'rb')
		try:
			config = pickle.load(config_file)
		except pickle.PickleError:
			save_config(config)
	except IOError:
		save_config(config)
	else:
		config_file.close()

	return config

def save_config(config):
	with open(config_file_path, 'wb') as config_file:
		try:
			pickle.dump(config, config_file, pickle.HIGHEST_PROTOCOL)
		except pickle.PickleError as err:
			print "Error: Couldn't write in {}".format(config_file_path)

def set_path(var_name, path):
	var_name = var_name.lower()

	if os.path.isdir(path):
		config = load_config()
		path = os.path.abspath(path)
		
		config['paths'][var_name] = path
		save_config(config)

		print '"{}" saved as "{}"'.format(path, var_name)
	else:
		print '"{}" does not seem to be a directory'.format(path)

def unset_path(var_name):
	var_name = var_name.lower()

	config = load_config()

	try:
		path = config['paths'].pop(var_name)
		save_config(config)

		print '"{}" has been unset'.format(var_name)
	except KeyError:
		print 'Error: path variable "{}" does not exist'.format(var_name)
	
def show_paths():
	config = load_config()

	for var, path in config['paths'].iteritems():
		print '{}="{}"'.format(var, path)


def open_dir(path):
	config = load_config()

	if path in config['paths']:
		launch(config['paths'][path])
	else:
		print 'Error: "{}" is not a valid path variable'.format(path)

def initialize_memory():
	global memory

	memory = [[-1] * MEMORY_SIZE for x in range(MEMORY_SIZE)]

if __name__ == '__main__':

	program_dir = os.path.dirname(os.path.realpath(__file__))
	config_file_path = os.path.join(program_dir, CONFIG_FILE_NAME)
				
	# TODO: make a proper parsing for this. argparse and docop don't seem to work
	args = sys.argv[1:]

	if len(args) > 0:
		if args[0] in ['set', 'unset', 'echo', 'open']:
			command = args[0]
			if command == 'set':
				if len(args) == 3:
					set_path(args[1], args[2])
			elif command == 'unset':
				if len(args) == 2:
					unset_path(args[1])
			elif command == 'echo':
				if len(args) == 1:
					show_paths()
			elif command == 'open':
				if len(args) == 2:
					open_dir(args[1])
		else:
			if len(args) > 1:
				search_for_directory = (args[0] == '-d')

				if len(args) == 2:
					if search_for_directory:
						search(None, args[1], True)
					else:
						search(args[0], args[1], False)
				elif len(args) == 3:
					search(args[1], args[2], search_for_directory)

			elif len(args) == 1:
				search(None, args[0], False)
	else:
		print doc
		