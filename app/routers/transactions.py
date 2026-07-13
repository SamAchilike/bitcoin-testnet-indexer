from fastapi import APIRouter, HTTPException
from app.models.transactions import Transaction
from app.crud_operations import get_transactions_by_block_height, get_transaction_by_txid

router = APIRouter()

@router.get("/transactions/block/{height}", response_model=list[Transaction])
def get_transactions_for_block(height: int):
    transactions = get_transactions_by_block_height(height)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this block")
    return transactions

@router.get("/transactions/{txid}", response_model=Transaction)
def get_transaction_by_id(txid: str):
    transaction = get_transaction_by_txid(txid) 
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction