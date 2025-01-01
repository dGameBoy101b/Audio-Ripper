from logging import DEBUG
from multiprocessing import current_process
from os.path import join, dirname

from ..exclude_filter import ExcludeFilter

from .formatted_path import FormattedPath

def get_filename_kwargs()->dict:
	return {
		'processName': current_process().name
	}

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
			'filename': FormattedPath(join(dirname(__file__), 'rip_gui_worker_{processName}.log'), kwargs_factory=get_filename_kwargs),
			'mode' : 'w',
			'filters':[
				'not_ffprobe'
			]
		}
	},
	'loggers':{
		'root':{
			'level':DEBUG,
			'handlers':[
				'file'
			]
		}
	}
}
	