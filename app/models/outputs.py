from pydantic import BaseModel

class Output(BaseModel):
    txid: str
    output_index: int
    address: str | None
    value: float
