"""Module for handling API request"""

import uvicorn

from fastapi import FastAPI
from prisma import Prisma

app = FastAPI()

prisma = Prisma()


@app.on_event("startup")
async def startup_event():
    """
    Function for Connecting to prisma before starting the app.
    """
    await prisma.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Function for diconnecting to prisma before shutting down the app.
    """
    await prisma.disconnect()


@app.get("/api/trades")
async def get_all_trades():
    """Function for retrieving all trades."""
    trades = await prisma.trade.find_many()
    return trades


@app.get("/api/trades/{block_number}")
async def get_trades_by_block(block_number: int):
    """Function for retrieving trades in a specific block."""
    trades = await prisma.trade.find_many(where={"block_number": block_number})
    return trades


@app.get("/api/trades/account/{account}")
async def get_trades_by_account(account: str):
    """Function for retrieving trades of a specific account."""
    trades = await prisma.trade.find_many(where={"account": account})
    return trades


@app.get("/api/position_settled")
async def get_position_settled():
    """Function for retrieving all settled trades."""
    trades = await prisma.position_settled.find_many()
    return trades


@app.get("/api/position_settled/{block_number}")
async def get_position_settled_by_block(block_number: int):
    """Function for retrieving all settled trades in a specific block."""
    trades = await prisma.position_settled.find_many(
        where={"block_number": block_number}
    )
    return trades


@app.get("/api/position_settled/account/{account}")
async def get_position_settled_by_account(account: str):
    """Function for retrieving all settled trades of a specific account."""
    trades = await prisma.position_settled.find_many(where={"account": account})
    return trades


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
