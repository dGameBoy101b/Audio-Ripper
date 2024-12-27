from logging import DEBUG, INFO, WARNING
from os.path import join, dirname
from sys import stderr, stdout

from ..max_level_filter import MaxLevelFilter
from ..exclude_filter import ExcludeFilter

config_dict = {
	'version': 1,
	'formatters':{
		'default' : {
			'format': "[{asctime}]{levelname}:{name}:{msg}",
			'style': "{"
		}
	},
	'filters':{
		'not_ffprobe':{
			'()': ExcludeFilter,
			'name': 'ffprobe'
		},
		'max_level_info':{
			'()': MaxLevelFilter,
			'level': INFO
		}
	},
	'handlers':{
		'file':{
			'class': 'logging.FileHandler',
			'formatter': 'default',
			'level': DEBUG,
			'filename': join(dirname(__file__), 'rip_gui.log'),
			'mode' : 'w',
			'filters':[
				'not_ffprobe'
			]
		},
		'info_console':{
			'class': 'logging.StreamHandler',
			'formatter': 'default',
			'level': INFO,
			'stream': stdout,
			'filters':[
				'not_ffprobe',
				'max_level_info'
			]
		},
		'error_console':{
			'class': 'logging.StreamHandler',
			'formatter': 'default',
			'level': WARNING,
			'stream': stderr,
			'filters':[
				'not_ffprobe'
			]
		}
	},
	'loggers':{
		'root':{
			'level':DEBUG,
			'handlers':[
				'file',
				'info_console',
				'error_console'
			]
		}
	}
}
	