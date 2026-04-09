from pydantic import BaseModel


class StaticInputs(BaseModel):
	use_smartds: bool = True
	user_uploads_model: bool = False
	profile_location: str = "SMART-DS/v1.0/2017/SFO/P1U/profiles"
	opendss_location: str = "SMART-DS/v1.0/2017/SFO/P1U/scenarios/solar_medium_batteries_none_timeseries/opendss/p1uhs0_1247/p1uhs0_1247--p1udt942"
	start_date: str = "2017-05-01 14:00:00"
	number_of_timesteps: int = 8
	run_freq_sec: int = 900
	topology_output: str = "./topology.json"
	name: str = "feeder"
	broker_address:str = "localhost"
	port:int = 23404
