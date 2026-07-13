import requests
import os
from dotenv import load_dotenv
from app.models.blocks import Block
from app.models.transactions import Transaction
from app.models.outputs import Output

load_dotenv()

rpc_url = os.getenv('QUICKNODE_URL')

def rpc_call(method, params=[]):

    """
    This function makes a JSON-RPC call to the blockchain node.
    :param method: The RPC method to call (e.g., "getblockcount", "getblockhash", "getblock")
    :param params: A list of parameters to pass to the RPC method

    You can check visit https://developer.bitcoin.org/reference/rpc.html for more details on available RPC methods and their parameters.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    response = requests.post(rpc_url, json=payload)
    return response.json()["result"]

def get_block_count() -> int | None:
    """
    This function retrieves the current block count from the blockchain node.
    From this we can check the current height of the blockchain and use it to fetch blocks in a loop.
    """
    try:
        return rpc_call("getblockcount")
    except Exception as e:
        print(f"Error fetching block count: {e}")
        return None

def get_block(height: int)-> tuple[Block, list[tuple[Transaction, list[Output]]]]:
    """
    This function retrieves a block by its height and returns a Block and a list of Transaction objects, which are defined in the models/blocks.py and models/transactions.py file.
    This allows us to get Block data, all the transactions in the block data, and all the outputs in each transaction via one RPC call, whereas we would have had to have written a function for 
    get_transaction and consumed API tokens for more rpc calls.
    """
    try:
        block_hash = rpc_call("getblockhash", [height])
        verbosity = 2 # To include transaction data into the block
        raw_block = rpc_call("getblock", [block_hash, verbosity])

        block = Block(
            hash=raw_block["hash"],
            height=raw_block["height"],
            tx_count=raw_block["nTx"],
            timestamp=raw_block["time"],
            size=raw_block["size"],
            previous_hash=raw_block.get("previousblockhash", "") # In case this is the genesis block which doesn't have a previous hash
        )
        raw_tx_list = raw_block["tx"]
        tx_objects = []

        for tx in raw_tx_list:
            transaction = Transaction(
                txid=tx["txid"],
                block_hash=raw_block["hash"],
                block_height=raw_block["height"],
                input_count=len(tx["vin"]),
                output_count=len(tx["vout"]),
                total_output_value=sum(output["value"] for output in tx["vout"])
            )

            outputs = []
            for output in tx["vout"]:
                try: 
                    address = output["scriptPubKey"].get("address", None)
                    outputs.append(Output(
                        txid=transaction.txid,
                        output_index=output["n"],
                        address=address,
                        value=output["value"]
                    ))
                except Exception as e:
                    print(f"Error processing output {output['n']} of transaction {transaction.txid}: {e}")
                    continue

            tx_objects.append((transaction, outputs))

        return (block, tx_objects)
    
    except Exception as e:
        print(f"Error fetching block at height {height}: {e}")
        return None



if __name__ == "__main__":
    # raw_block = rpc_call("getblock", [rpc_call("getblockhash", [109])])
    # first_txid = raw_block["tx"][0]
    # result = get_transaction(first_txid, raw_block["hash"], 109)
    # if result:
    #     transaction, outputs = result
    #     print(f"Transaction: \n{transaction}\n")
    #     print(f"Outputs: \n{outputs}")


    # else:
    #     print(f"Failed to fetch transaction {first_txid}")
    pass