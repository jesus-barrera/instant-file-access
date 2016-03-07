import os
import platform
from modules.parse import parse, Search, Subcommand
from modules.config import load_config, save_config

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

MEMORY_SIZE = 250

list_results = False
memory = []
		
def do_search(search_root, search_pattern, search_for_directory):
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

def show_paths():
	config = load_config()

	for var, path in config['paths'].iteritems():
		print '{}="{}"'.format(var, path)

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
	res = parse(doc)

	if (isinstance(res, Search)):
		options = res.opts
		search_directory = False

		if '-d' in options or '--directory' in options:
			search_directory = True

		do_search(res.root, ' '.join(res.words), search_directory)

	elif(isinstance(res, Subcommand)):
		cmd = res.cmd
		args = res.args

		if cmd == 'set':
			set_path(args['var_name'], args['path'])
		elif cmd == 'unset':
			unset_path(args['var_name'])
		elif cmd == 'echo':
			show_paths()
		elif cmd == 'open':
			open_dir(args['var_name'])
		
