"""Module for handling the trades and writing into database"""

from prisma.errors import PrismaError

from logger import log_message
from prisma import Prisma

from handlers.position_settled_handler import pos_settled,pos_open,pos_inc,pos_dec

# Initialize Prisma client
prisma = Prisma()


async def counter(trade_data, transaction):
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
                await transaction.token_count.update_many(
                    where={"link": link, "token": token},
                    data={"count": new_count},
                )
            except PrismaError:
                data = {"link": link, "token": token, "count": new_count}
                await transaction.token_count.create(data=data)
            finally:
                await transaction.position_count.update_many(
                    where={"link": link}, data={"count": new_count}
                )
            return new_count
        except PrismaError:
            pos_data = {"link": link, "count": 1}
            data = {"link": link, "token": token, "count": 1}
            await transaction.token_count.create(data=data)
            await transaction.position_count.create(data=pos_data)
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


async def write(trade_data, transaction):
    """
    Appends a row of trade to the database.
    Args:
        trade_data: List containing trade information to be written to the database.
    """
    link_counter = await counter(trade_data[0], transaction)
    if link_counter is not None:
        trade_data[0]["link"] = (
            "PositionLink_" + str(link_counter) + "_0x" + str(trade_data[0]["link"])
        )
        await transaction.trade.create(data=trade_data[0])
        if trade_data[0]["events"] in ("Close", "Liqudated"):
            position_details = await prisma.position_unsettled.find_first_or_raise(
                where={
                    "link": trade_data[0]["link"],
                }
            )
            settled_data = pos_settled(trade_data, position_details)
            await transaction.position_settled.create(data=settled_data)
            log_message(
                "info",
                "Position Settled for transaction hash %s and log index %s.",
                trade_data[0]["transaction_hash"],
                trade_data[0]["log_index"],
            )
        elif trade_data[0]["events"] == "Open":
            open_data = pos_open(trade_data)
            await transaction.position_unsettled.create(data=open_data)
        elif trade_data[0]["events"] == "Increase":
            pos_data = await prisma.position_unsettled.find_first_or_raise(
                where={
                    "link": trade_data[0]["link"],
                }
            )
            unsettled_data = pos_inc(pos_data, trade_data)
            await transaction.position_unsettled.update_many(
                where={
                    "link": trade_data[0]["link"],
                },
                data=unsettled_data,
            )
        else:
            pos_data = await prisma.position_unsettled.find_first_or_raise(
                where={
                    "link": trade_data[0]["link"],
                }
            )
            unsettled_data = pos_dec(pos_data, trade_data)
            await transaction.position_unsettled.update_many(
                where={
                    "link": trade_data[0]["link"],
                },
                data=unsettled_data,
            )


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
                                "transaction_hash": trade_data[0]["transaction_hash"],
                                "log_index": trade_data[0]["log_index"],
                            }
                        )
                        if not trade:
                            await write(trade_data, transaction)
                            log_message(
                                "info",
                                "Trade added successfully with data: %s.",
                                trade_data[0],
                            )
                        else:
                            log_message(
                                "info",
                                "Trade already exists for transaction hash %s and log index %s.",
                                trade_data[0]["transaction_hash"],
                                trade_data[0]["log_index"],
                            )

                except PrismaError as e:
                    log_message(
                        "error",
                        "An error occurred with transaction hash %s and log index %s: %s",
                        trade_data[0]["transaction_hash"],
                        trade_data[0]["log_index"],
                        e,
                    )
                    print("here")
                    return
        await prisma.block.update_many(
            where={"id": 1}, data={"last_update": last_block}
        )
        log_message("info", "Last synced block %d", last_block - 1)
    except PrismaError as e:
        log_message("error", "An error occurred: %s", e)
    finally:
        await prisma.disconnect()
