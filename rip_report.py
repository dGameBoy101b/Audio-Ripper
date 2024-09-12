from dataclasses import dataclass
from pathlib import PurePath
from rip_args import RipArgs

@dataclass(frozen=True)
class RipReport:
	args: RipArgs
	conversions:dict
	seconds_to_rip:float

	def __str__(self)->str:
		return (f'{self.args}'
		+f'\n{len(self.conversions)} conversions:\n'+'\n'.join([f'\t{input} -> {output}' for (input, output) in self.conversions.items()])
		+f'\ntook {self.seconds_to_rip} seconds')
