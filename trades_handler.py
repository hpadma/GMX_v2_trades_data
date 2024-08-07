"""Module for handling the trades and writing into database"""

from prisma.errors import PrismaError

from logger import log_message
from prisma import Prisma

# Initialize Prisma client
prisma = Prisma()


async def counter(trade_data):
    """
    Updates and returns the position link count for each link.
    Args:
        trade_data: List containing trade information.
    Returns:
        int: Position count of link
    """
    events = trade_data["events"]
    token = trade_data["token"]
    link = trade_data["link"]

    if events == "Open":
        try:
            pos_data = await prisma.position_count.find_first_or_raise(
                where={"link": link}
            )
            new_count = pos_data.count + 1
            try:
                await prisma.token_count.update_many(
                    where={"link": link, "token": token},
                    data={"count": new_count},
                )
            except PrismaError:
                data = {"link": link, "token": token, "count": new_count}
                await prisma.token_count.create(data=data)
            finally:
                await prisma.position_count.update_many(
                    where={"link": link}, data={"count": new_count}
                )
            return new_count
        except PrismaError:
            pos_data = {"link": link, "count": 1}
            data = {"link": link, "token": token, "count": 1}
            await prisma.token_count.create(data=data)
            await prisma.position_count.create(data=pos_data)
            return 1
    else:
        try:
            data = await prisma.token_count.find_first_or_raise(
                where={"link": link, "token": token}
            )
            return data.count
        except PrismaError:
            log_message(
                "warning",
                "Missing Open position of trade with transaction hash %s and log index %s.",
                trade_data["transaction_hash"],
                trade_data["log_index"],
            )
            return None


async def write(trade_data):
    """
    Appends a row of trade to the database.
    Args:
        trade_data: List containing trade information to be written to the database.
    """
    link_counter = await counter(trade_data)
    if link_counter is not None:
        trade_data["link"] = (
            "PositionLink_" + str(link_counter) + "_0x" + str(trade_data["link"])
        )
        await prisma.trade.create(data=trade_data)


async def handle_trades(all_trades, last_block):
    """
    Updates the position link and writes the trade data to the database.
    Args:
        all_trades: List of trades to process.
        last_block: The last block number to update.
    """
    try:
        await prisma.connect()
        for trades in all_trades:
            for trade_data in trades:
                try:
                    async with prisma.tx() as transaction:
                        trade = await transaction.trade.find_many(
                            where={
                                "transaction_hash": trade_data["transaction_hash"],
                                "log_index": trade_data["log_index"],
                            }
                        )
                        if not trade:
                            await write(trade_data)
                            log_message(
                                "info",
                                "Trade added successfully with data: %s.",
                                trade_data,
                            )
                        else:
                            log_message(
                                "info",
                                "Trade already exists for transaction hash %s and log index %s.",
                                trade_data["transaction_hash"],
                                trade_data["log_index"],
                            )
                except PrismaError as e:
                    log_message(
                        "error",
                        "An error occurred with transaction hash %s and log index %s: %s",
                        trade_data["transaction_hash"],
                        trade_data["log_index"],
                        e,
                    )
        await prisma.block.update_many(
            where={"id": 1}, data={"last_update": last_block}
        )
        log_message("info", "Last synced block %d", last_block - 1)
    except PrismaError as e:
        log_message("error", "An error occurred: %s", e)
    finally:
        await prisma.disconnect()
