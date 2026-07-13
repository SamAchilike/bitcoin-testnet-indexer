import time
from app.database import get_connection, create_block_table, create_transaction_table, create_outputs_table
from app.crud_operations import insert_block, insert_transaction, insert_output, get_last_indexed_height
from app.rpc import get_block, get_block_count

SLEEP_BETWEEN_BLOCKS = 0.1      # seconds between each block
LIVE_SYNC_INTERVAL = 300        # seconds between live sync polls (5 minutes)

def index_block(height: int, connection):
    """Fetches a single block and all its transactions and outputs, then stores them atomically."""
    
    result = get_block(height)
    if result is None:
        print(f"Retrying Block index at height {height}...")

        for _ in range(3):
            result = get_block(height)
            time.sleep(2.0)

            if result is not None:
                print(f"Successful retry for block {height}")
                break
            
    if result is None:
        print(f"Failed to fetch block at height {height}, skipping...")
        return False

    block, tx_objects = result

    insert_block(block, connection)

    for transaction, outputs in tx_objects:
        insert_transaction(transaction, connection)
        for output in outputs:
            insert_output(output, connection)

    return True


def run_historical_sync():
    """Indexes all blocks from the last indexed height to the current chain tip."""

    start_height = get_last_indexed_height()
    end_height = get_block_count()

    if end_height is None:
        print("Could not get current block count. Aborting.")
        return

    if start_height >= end_height:
        print("Already synced to chain tip.")
        return

    print(f"Starting historical sync from block {start_height} to {end_height}...")

    for height in range(start_height, end_height + 1):
        connection = get_connection()
        if connection is None:
            print(f"Could not connect to database at block {height}. Retrying next cycle.")
            continue

        try:
            success = index_block(height, connection)
            if success:
                connection.commit()
                print(f"Indexed block {height}/{end_height}")
            else:
                connection.rollback()

        except Exception as e:
            connection.rollback()
            print(f"Error indexing block {height}: {e}")

        finally:
            connection.close()

        time.sleep(SLEEP_BETWEEN_BLOCKS)

    print("Historical sync complete.")


def run_live_sync():
    """Polls for new blocks every LIVE_SYNC_INTERVAL seconds and indexes them."""

    print("Starting live sync...")

    while True:

        last_indexed = get_last_indexed_height()
        current_tip = get_block_count()

        if current_tip is None:
            print("Could not reach QuickNode. Will retry.")
            continue

        if current_tip > last_indexed:
            print(f"New blocks found: {last_indexed + 1} to {current_tip}. Indexing...")
            run_historical_sync()
        else:
            print(f"No new blocks. Current tip: {current_tip}")
        
        time.sleep(LIVE_SYNC_INTERVAL)


def get_missing_heights() -> list[int]:

    """Returns a list of block heights that are missing in the 'blocks' table"""

    connection = get_connection()
    if connection is None:
        return []
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT generate_series AS missing_height
                FROM generate_series(0, (SELECT MAX(height) FROM blocks))
                LEFT JOIN blocks ON height = generate_series
                WHERE height IS NULL
                ORDER BY missing_height
            """)
            results = cursor.fetchall()
            return [row[0] for row in results]
    except Exception as e:
        print(f"Error detecting gaps: {e}")
        return []
    finally:
        connection.close()


def index_missing_blocks():
    """Finds and re-indexes any gaps in the blocks table."""

    missing = get_missing_heights()
    
    if not missing:
        print("No gaps found.")
        return

    print(f"Found {len(missing)} missing blocks: {missing}")

    for height in missing:
        connection = get_connection()
        if connection is None:
            print(f"Could not connect to database for gap block {height}. Skipping for now.")
            continue

        try:
            success = index_block(height, connection)
            if success:
                connection.commit()
                print(f"Filled gap at block {height}")
            else:
                connection.rollback()
                print(f"Still could not fill gap at block {height}")

        except Exception as e:
            connection.rollback()
            print(f"Error filling gap at block {height}: {e}")

        finally:
            connection.close()

        time.sleep(SLEEP_BETWEEN_BLOCKS)

    print("Gap filling complete.")


def start_indexer():
    """Entry point for the indexer."""

    create_block_table()
    create_transaction_table()
    create_outputs_table()

    index_missing_blocks()
    run_historical_sync()
    run_live_sync()


