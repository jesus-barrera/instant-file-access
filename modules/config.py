import pickle
import os

CONFIG_FILE_NAME = '../ifa.conf'

program_dir = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.path.join(program_dir, CONFIG_FILE_NAME)

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