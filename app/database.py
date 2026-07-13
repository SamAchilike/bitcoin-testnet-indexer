from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

host = os.getenv('DB_HOST')
port = os.getenv('PORT')
dbname = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

def get_connection():
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def create_block_table():
    connection = get_connection()
    if connection is None:
        return

    try:
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS blocks (
                hash VARCHAR(64) PRIMARY KEY,
                height INTEGER NOT NULL,
                tx_count INTEGER NOT NULL,
                timestamp FLOAT NOT NULL,
                size INTEGER NOT NULL,
                previous_hash VARCHAR(64)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
    except Exception as e:
        print(f"Error creating blocks table: {e}")
    finally:
        connection.close()

def create_transaction_table():
    connection = get_connection()
    if connection is None:
        return

    try:
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS transactions (
                txid VARCHAR(64) PRIMARY KEY,
                block_hash VARCHAR(64) NOT NULL,
                block_height INTEGER NOT NULL,
                input_count INTEGER NOT NULL,
                output_count INTEGER NOT NULL,
                total_output_value FLOAT NOT NULL,
                FOREIGN KEY (block_hash) REFERENCES blocks(hash)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
    except Exception as e:
        print(f"Error creating transactions table: {e}")
    finally:
        connection.close()

def create_outputs_table():
    connection = get_connection()
    if connection is None:
        return

    try:
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS outputs (
                txid VARCHAR(64) NOT NULL,
                output_index INTEGER NOT NULL,
                address VARCHAR(255),
                value FLOAT NOT NULL,
                PRIMARY KEY (txid, output_index),
                FOREIGN KEY (txid) REFERENCES transactions(txid)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
    except Exception as e:
        print(f"Error creating outputs table: {e}")
    finally:
        connection.close()
