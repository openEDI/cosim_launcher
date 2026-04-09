from typing import Dict, List

from pydantic import BaseModel


class StaticInputs(BaseModel):
	start_date:str | None = None
	run_freq_sec:int = 900
	start_time_index:int = 0
	number_of_timesteps:int = 8

class InputMapping(BaseModel):
	powers_real: str
	powers_imaginary: str
	topology: str

class Component(BaseModel):
	name:str
	type:str
	parameters:Dict

class Link(BaseModel):
	source:str
	source_port:str
	target:str
	target_port:str

class WiringDiagram(BaseModel):
	name:str
	components:List[Component]
	links:List[Link]

