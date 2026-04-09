from pydantic import BaseModel


class StaticInputs(BaseModel):
	feather_filename:str = "output.feather"
	csv_filename:str = "output.csv"
	name:str = "recorder"
	broker_address:str = "localhost"
	port:int = 23404

class InputMapping(BaseModel):
	subscription: str = ""
