from pydantic import BaseModel

class Block(BaseModel):
    hash: str
    height: int
    tx_count: int
    timestamp: float
    size: int
    previous_hash: str

