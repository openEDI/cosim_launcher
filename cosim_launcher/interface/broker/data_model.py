from pydantic import BaseModel


class StaticInputs(BaseModel):
	number_of_federates: int

