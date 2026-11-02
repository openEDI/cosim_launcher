from pydantic import BaseModel


class StaticInputs(BaseModel):
	feather_filename:str = "ieee123_power_system_injection_predictor.h5"
	nonZeroIdx:list = [18, 108, 162, 183, 207, 222, 264, 282, 366]
	totInjCol:int = 396
	n_buses:int = 132
	n_phases:int = 3
	broker_address:str = 'localhost'
	port:int = 23404

class InputMapping(BaseModel):
	powers_real_sensor: str
	powers_imaginary_sensor: str
