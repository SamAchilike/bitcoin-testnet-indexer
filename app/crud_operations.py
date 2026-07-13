from app.database import create_outputs_table, get_connection, create_block_table, create_transaction_table
from app.models.blocks import Block
from app.models.transactions import Transaction
from app.models.outputs import Output
from psycopg2.extras import RealDictCursor

def create_tables():
    create_block_table()
    create_transaction_table()
    create_outputs_table()

def insert_block(block: Block, connection) -> Block | None:
    """ This function takes a Block object and inserts it into the blocks table in the database. """
    
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:

        insert_query = """
        INSERT INTO blocks (hash, height, tx_count, timestamp, size, previous_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (hash) DO NOTHING
        RETURNING *
        """

        insert_values = (block.hash, block.height, block.tx_count, block.timestamp, block.size, block.previous_hash)
        cursor.execute(insert_query, insert_values)
        new_block = cursor.fetchone()
    return new_block

def insert_transaction(transaction: Transaction, connection) -> Transaction | None:
    """ This function takes a Transaction object and inserts it into the transactions table in the database. """
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:

        insert_query = """
        INSERT INTO transactions (txid, block_hash, block_height, input_count, output_count, total_output_value)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (txid) DO NOTHING
        RETURNING *
        """

        insert_values = (
            transaction.txid, 
            transaction.block_hash, 
            transaction.block_height, 
            transaction.input_count,
            transaction.output_count,
            transaction.total_output_value
            )
        cursor.execute(insert_query, insert_values)
        new_transaction = cursor.fetchone()
    return new_transaction

def insert_output(output: Output, connection) -> Output | None:
    """ This function takes an Output object and inserts it into the outputs table in the database. """
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        insert_query = """
        INSERT INTO outputs (txid, output_index, address, value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (txid, output_index) DO NOTHING
        RETURNING *
        """

        insert_v_alues = (output.txid, output.output_index, output.address, output.value)
        cursor.execute(insert_query, insert_values)
        new_output = cursor.fetchone()
    return new_output

def get_last_indexed_height()-> int:
    """ This function retrieves the height of the last indexed block from the database. """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            query = "SELECT MAX(height) FROM blocks"
            cursor.execute(query)
            result = cursor.fetchone()[0]

    if result is not None:
        return result
    return 0

def block_exists(hash):
    """Checks if a block with the given hash already exists in the database to avoid duplicates."""

    with get_connection() as connection:
        with connection.cursor() as cursor:
            query = "SELECT 1 FROM blocks WHERE hash = %s"
            cursor.execute(query, (hash,))
            exists = cursor.fetchone() is not None

    return exists

def get_block_by_hash(hash: str) -> Block | None:
    """ This function retrieves a block from the database by its hash. """

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM blocks WHERE hash = %s"
            cursor.execute(query, (hash,))
            result = cursor.fetchone()

    if result:
        return Block(**result)
    return None

def get_block_by_height(height: int) -> Block | None:
    """ This function retrieves a block from the database by its height. """

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM blocks WHERE height = %s"
            cursor.execute(query, (height,))
            result = cursor.fetchone()

    if result:
        return Block(**result)
    return None

def fetch_blocks_by_range(start: int, stop: int) -> list[Block]:
    """ This function retrieves a list of blocks from the database within a specified range of block heights. """

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM blocks WHERE height BETWEEN %s AND %s ORDER BY height ASC"
            cursor.execute(query, (start, stop))
            results = cursor.fetchall()

    return [Block(**result) for result in results]

def get_transactions_by_block_height(height: int) -> list[Transaction]:
    """Get a list of transactions within a block"""

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM transactions WHERE block_height =%s ORDER BY txid"
            cursor.execute(query, (height,))
            results = cursor.fetchall()

    return [Transaction(**result) for result in results]

def get_transaction_by_txid(txid: str) -> Transaction | None:
    """Get a single transaction by its txid"""

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM transactions WHERE txid = %s"
            cursor.execute(query, (txid,))
            result = cursor.fetchone()

    if result:
        return Transaction(**result)
    return None

def get_outputs_by_txid(txid: str) -> list[Output]:
    """Get a list of Outputs from within a specific transaction"""

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM outputs WHERE txid =%s"
            cursor.execute(query, (txid,))
            results = cursor.fetchall()

    return [Output(**result) for result in results]

def get_outputs_by_address(address: str) -> list[Output]:
    """Get a list of Outputs sent to a particular address"""

    with get_connection() as connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = "SELECT * FROM outputs WHERE address = %s"
            cursor.execute(query, (address,))
            results = cursor.fetchall()

    return [Output(**result) for result in results]