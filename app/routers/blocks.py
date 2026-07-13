from fastapi import APIRouter, HTTPException
from app.models.blocks import Block
from app.crud_operations import get_last_indexed_height, get_block_by_hash, get_block_by_height, fetch_blocks_by_range

router = APIRouter()

@router.get("/blocks/latest", response_model=Block)
def get_latest_block():
    latest_height = get_last_indexed_height()

    if latest_height == 0:
        raise HTTPException(status_code=404, detail="No blocks indexed yet")
    return get_block_by_height(latest_height)

@router.get("/blocks/last-indexed-height")
def last_indexed_height():
    return {"last-indexed-height": get_last_indexed_height()}

@router.get("/blocks/block/{hash}")
def fetch_block_by_hash(hash: str):

    block = get_block_by_hash(hash)
    if block:
        return block
    raise HTTPException(status_code=404, detail="Block not found in database")

@router.get("/blocks/{start}-{stop}", response_model=list[Block])
def get_blocks_by_range(start: int, stop: int):
    return fetch_blocks_by_range(start, stop)

@router.get("/blocks/height/{height}", response_model=Block)
def get_block_at_height(height: int):
    block = get_block_by_height(height)
    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")
    return block