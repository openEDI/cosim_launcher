from typing import Dict, List

from pydantic import BaseModel


class StaticInputs(BaseModel):
	sensor_list: List[str] = []
	measurement_file:str = "sensor_list.json"
	name:str = "sensor"
	additive_noise_stddev: float = 0.0
	broker_address:str = "localhost"
	port:int = 23404

class InputMapping(BaseModel):
	subscription: str = ""
