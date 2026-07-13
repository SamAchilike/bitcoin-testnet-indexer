from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio

from app.database import create_block_table, create_transaction_table, create_outputs_table
from app.indexer import start_indexer
from app.routers import blocks, transactions, outputs

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_block_table()
    create_transaction_table()
    create_outputs_table()

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, start_indexer)

    yield  

app = FastAPI(lifespan=lifespan)

app.include_router(blocks.router)
app.include_router(transactions.router)
app.include_router(outputs.router)