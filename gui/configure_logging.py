from logging import DEBUG, INFO
from os.path import join, dirname
from sys import stdout
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
		'console':{
			'class': 'logging.StreamHandler',
			'formatter': 'default',
			'level': INFO,
			'stream': stdout,
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
				'console'
			]
		}
	}
}
	