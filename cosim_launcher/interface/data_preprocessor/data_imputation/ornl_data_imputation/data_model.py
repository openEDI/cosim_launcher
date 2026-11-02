from pydantic import BaseModel

from ornl_pow_imputation.config import ImputerConfig

class StaticInputs(BaseModel,ImputerConfig):
	start_date:str | None = None
	run_freq_sec:int = 900
	start_time_index:int = 0
	number_of_timesteps:int = 8
	broker_address:str = "localhost"
	port:int = 23404


class InputMapping(BaseModel):
	powers_real: str
	powers_imaginary: str
	voltages_real: str
	voltages_imaginary: str
