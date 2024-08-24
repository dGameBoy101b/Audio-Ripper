import ffmpeg

#https://github.com/kkroening/ffmpeg-python/issues/112
def override_media_metadata(**overrides)->dict[str, str]:
	args=dict({'map_metadata':0})
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
