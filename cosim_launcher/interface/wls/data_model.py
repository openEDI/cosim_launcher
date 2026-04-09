from typing import Dict, List

from pydantic import BaseModel


class StaticInputs(BaseModel):
	name: str = "wls"
	broker_address:str = "localhost"
	port:int = 23404

class InputMapping(BaseModel):
	voltages_magnitude: str
	powers_real: str
	powers_imaginary: str
	topology: str
