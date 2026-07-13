from fastapi import APIRouter, HTTPException
from app.models.outputs import Output
from app.crud_operations import get_outputs_by_txid, get_outputs_by_address

router = APIRouter()

@router.get("/outputs/block/{txid}", response_model=list[Output])
def fetch_outputs_for_txid(txid: str):
    outputs = get_outputs_by_txid(txid)
    if not outputs:
        raise HTTPException(status_code=404, detail="No transactions found for this block")
    return outputs

@router.get("/outputs/address/{address}", response_model=list[Output])
def get_outputs_for_address(address: str):
    outputs = get_outputs_by_address(address)  # new crud function needed
    if not outputs:
        raise HTTPException(status_code=404, detail="No outputs found for this address")
    return outputs

