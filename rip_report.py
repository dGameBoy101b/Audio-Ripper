from dataclasses import dataclass
from pathlib import PurePath

@dataclass(frozen=True)
class RipReport:
	output_dir:PurePath
	input_dir:PurePath
	output_extension:str
	metadata_overrides:dict
	metadata_args:dict
	conversions:dict
	seconds_to_rip:float

	def __str__(self)->str:
		return (f'{self.input_dir} -> {self.output_dir / ('*' if self.output_extension is None else '*'+self.output_extension)}'
		+f'\n{len(self.metadata_overrides)} metadata overrides:\n'+'\n'.join([f'\t{key}={'' if value is None else value}' for (key,value) in self.metadata_overrides.items()])
		+f'\n{len(self.conversions)} conversions:\n'+'\n'.join([f'\t{input} -> {output}' for (input, output) in self.conversions.items()])
		+f'\ntook {self.seconds_to_rip} seconds')
