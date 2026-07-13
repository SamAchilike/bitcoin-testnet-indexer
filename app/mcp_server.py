from fastmcp import FastMCP
from app.crud_operations import get_last_indexed_height, get_block_by_hash, get_block_by_height, fetch_blocks_by_range, get_transaction_by_txid, get_transactions_by_block_height, get_outputs_by_txid, get_outputs_by_address
from app.models.blocks import Block
from app.models.transactions import Transaction
from app.models.outputs import Output

mcp = FastMCP(
    name="BTC Testnet 4 Indexer MCP Server",
    instructions= "This is an MCP server that helps a user to query the an indexed databased with prompts.\n"
"Your job is to call the tools that can help the user to make any such queries.")

@mcp.tool()
def mcp_get_block_by_height(height: int) -> Block | None:
    """Retrieve a Bitcoin block by its height from the indexed database."""
    block = get_block_by_height(height)
    return block

@mcp.tool()
def mcp_get_last_indexed_height() -> int:
    """Get the height of the last indexed height"""
    height = get_last_indexed_height()
    return height

@mcp.tool()
def mcp_get_block_by_hash(hash: str) -> Block | None:
    """Get a Block (a pydantic BaseModel with fields hash:str, height: int, tx_count: int, timestamp: float, size: int, previous_hash: str) by it's hash. """
    block = get_block_by_hash(hash)
    return block

@mcp.tool()
def mcp_fetch_blocks_by_range(start: int, stop: int) -> list[Block]:
    """Get a list of blocks based on the specified range from a start number to a stop number"""
    blocks = fetch_blocks_by_range(start, stop)
    return blocks

@mcp.tool()
def mcp_get_transaction_by_txid(txid: str)-> Transaction | None:
    """
    Get a transaction by it's txid.
    A transaction is a Transaction and is a pydantic BaseModel. 
    It looks like this:

    class Transaction(BaseModel):
        txid: str
        block_hash: str
        block_height: int
        input_count: int
        output_count: int
        total_output_value: float


    """
    tx = get_transaction_by_txid(txid)
    return tx

@mcp.tool()
def mcp_get_transactions_by_block_height(height: int)-> list[Transaction]:
    """Get a list of transactions that are inside a block from a particular height"""
    transactions = get_transactions_by_block_height(height)
    return transactions

@mcp.tool()
def mcp_get_outputs_by_txid(txid: str) -> list[Output]:
    """
    Get a list of outputs within a particular transaction
    Each output is of an Output type, a Pydantic BaseModel that looks like this:

    class Output(BaseModel):
        txid: str
        output_index: int
        address: str | None
        value: float
    """
    outputs = get_outputs_by_txid(txid)
    return outputs

@mcp.tool()
def mcp_get_outputs_by_address(address: str) -> list[Output]:
    """Get a list of Outputs sent to a particular address"""
    outputs = get_outputs_by_address(address)
    return outputs

def run_mcp():
    mcp.run(transport="http", host="127.0.0.1", port=8000)

if __name__ == "__main__":
    run_mcp()