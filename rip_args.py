from dataclasses import dataclass
from pathlib import PurePath
from .change_file_extension import change_file_extension
from .override_media_metadata import override_media_metadata

@dataclass(frozen=True)
class RipArgs:
	output_dir:PurePath
	input_dir:PurePath 
	output_extension:str|None 
	metadata_overrides:dict[str,any]
	output_args:dict[str,any]

	def __init__(self, output_dir:PurePath, input_dir:PurePath, output_extension:str|None, metadata_overrides:dict[str,any]):
		object.__setattr__(self, 'output_dir', PurePath(output_dir))
		object.__setattr__(self, 'input_dir', PurePath(input_dir))
		object.__setattr__(self, 'output_extension', None if output_extension is None else str(output_extension))
		if self.output_extension is not None and self.output_extension[0] != '.':
			object.__setattr__(self, 'output_extension', '.'+ output_extension)
		object.__setattr__(self, 'metadata_overrides', dict(metadata_overrides))
		object.__setattr__(self, 'output_args', override_media_metadata(**metadata_overrides))
		if output_extension is None:
			self.output_args['codec'] = 'copy'
		else:
			self.output_args['f'] = self.output_extension[1:]

	def output_path(self, input_path:PurePath)->PurePath:
		input_path = PurePath(input_path)
		filename = change_file_extension(self.output_dir / input_path.relative_to(self.input_dir), self.output_extension)
		return filename
	
	def __str__(self)->str:
		return (f'{self.input_dir} -> {self.output_dir / ('*' if self.output_extension is None else '*'+self.output_extension)}'
		+f'\n{len(self.metadata_overrides)} metadata overrides:'+''.join([f'\n\t{key}={'' if value is None else value}' for (key,value) in self.metadata_overrides.items()]))
