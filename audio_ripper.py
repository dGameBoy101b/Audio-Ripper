from argparse import ArgumentParser
import sys
from pathlib import PurePath
import logging
import rip

def create_parser()->ArgumentParser:
	logger = logging.getLogger(__name__)

	def convert_filetype(arg:str)->str|None:
		if arg == '':
			return None
		if arg[0] != '.':
			return '.'+arg
		return arg
	
	def convert_metadata_override(arg:str)->tuple[str,any]:
		key, value = arg.split('=', 1)
		if value == '':
			value = None
		return (key, value)
	
	logger.debug('creating argument parser...')
	parser = ArgumentParser( 
		description='Copies audio from an input directory to an output directory while overriding metadata.')
	logger.debug('adding output_dir argument...')
	parser.add_argument('output_dir', type=PurePath,
		help='The directory to copy to.')
	logger.debug('adding input_dir argument...')
	parser.add_argument('input_dir', nargs='?', default=PurePath('.'), type=PurePath, 
		help='The directory to copy from.'
		+'\nDefaults to the current directory.')
	logger.debug('adding output filetype argument...')
	parser.add_argument('-t', '--filetype', dest='output_filetype', nargs='?', default=None, type=convert_filetype, 
		help='The file extension to convert all files to.'
		+'\nUse an empty string (the default) to not convert file formats.')
	logger.debug('adding metadata overrides argument...')
	parser.add_argument('-m', '--metadata', dest='metadata_overrides', nargs='*', default=[], type=convert_metadata_override, 
		help='The key-value pairs used to override metadata in the form <key>=<value>.'
		+'\nBlank values ensure the associated key is deleted if it exists.'
		+'\nKeys that already exist will have their values overriden.'
		+'\nKeys that do not exist will be appended.')
	logger.debug('argument parser created')
	return parser

logger = logging.getLogger(__name__)
parser = create_parser()
sys_args = sys.argv[1:]
logger.debug(f'given commandline args: {sys_args}')
args = parser.parse_args(sys_args)
logger.debug(f'args parsed: {args}')
report = rip.rip(args.output_dir, args.input_dir, args.output_filetype, **dict(args.metadata_overrides))
logger.debug(f'rip complete: {report}')
print(report)