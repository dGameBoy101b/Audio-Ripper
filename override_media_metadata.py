def override_media_metadata(**overrides)->dict[str, str]:
	#some encoders dump metadata in the global container while others dump it in the stream so we need to copy both
	args=dict({ 
		'map_metadata:g':'0:g', #copy global metadata
		'map_metadata:g:':'0:s:a' #copy audio stream metadata
	})

	#https://github.com/kkroening/ffmpeg-python/issues/112
	index=0
	for key in overrides:
		args[f'metadata:g:{index}']=f'{key}={overrides[key]}' 
		index+=1
		
	return args

if __name__=='__main__':
	overrides = {'author':'me','year':'2024'}
	print(overrides)
	mapped = override_media_metadata(**overrides)
	print(mapped)
