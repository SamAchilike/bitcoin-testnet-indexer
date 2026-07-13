from pydantic import BaseModel

class Transaction(BaseModel):
    txid: str
    block_hash: str
    block_height: int
    input_count: int
    output_count: int
    total_output_value: float