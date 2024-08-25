from dataclasses import dataclass

@dataclass(frozen=True)
class RipReport:
	output_dir:str 
	input_dir:str
	output_extension:str
	metadata_overrides:dict
	metadata_args:dict
	conversions:dict

	def __str__(self)->str:
		return (f'{self.input_dir} -> {self.output_dir}/*{self.output_extension}'
		+f'\n{len(self.metadata_overrides)} metadata overrides:\n'+'\n'.join([f'\t{key}={value}' for (key,value) in self.metadata_overrides.items()])
		+f'\n{len(self.conversions)} conversions:\n'+'\n'.join([f'\t{input} -> {output}' for (input, output) in self.conversions.items()]))
