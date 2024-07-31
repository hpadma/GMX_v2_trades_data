"""Module for handling the trades and writing into database"""

from prisma.errors import PrismaError

from prisma import Prisma

# Initialize Prisma client
prisma = Prisma()


async def counter(trade_data):
    """
    Updates and returns the postion link count for each account.
    Args:
        trade_data: List containing trade information.
    Returns:
        int: Position count of link
    """
    events = trade_data["events"]
    token = trade_data["token"]
    account = trade_data["account"]

    # For the event Open increase the position link count else return present count
    if events == "Open":
        # Increase the count if link already exist else intiatiate it with 1
        try:
            pos_data = await prisma.position_count.find_first_or_raise(
                where={"account": account}
            )
            new_count = pos_data.count + 1
            try:
                data = await prisma.token_count.find_first_or_raise(
                    where={"account": account, "token": token}
                )
                await prisma.token_count.update_many(
                    where={"account": account, "token": token},
                    data={"count": new_count},
                )
            except PrismaError:
                data = {"account": account, "token": token, "count": new_count}
                await prisma.token_count.create(data=data)
            finally:
                await prisma.position_count.update_many(
                    where={"account": account}, data={"count": new_count}
                )
            return new_count
        except PrismaError:
            pos_data = {"account": account, "count": 1}
            data = {"account": account, "token": token, "count": 1}
            await prisma.token_count.create(data=data)
            await prisma.position_count.create(data=pos_data)
            return 1

    else:
        try:
            data = await prisma.token_count.find_first_or_raise(
                where={"account": account, "token": token}
            )
            return data.count
        except PrismaError:
            print("No open position for the Trade found")
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


async def handle_trades(trade_data):
    """
    Updates the position link and writes the trade data to the database.
    Args:
        trade_data: List containing trade information.
    """
    try:
        await prisma.connect()

        # Find trades with the specified transaction hash
        trade = await prisma.trade.find_many(
            where={"transaction_hash": trade_data["transaction_hash"]}
        )

        if trade == []:
            await write(trade_data)
            print("Trade added successfully")
        else:
            print("Trade already exist")
    except PrismaError as e:
        print(f"An error occurred: {e}")
    finally:
        await prisma.disconnect()
