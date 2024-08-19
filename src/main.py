"""Module for listening and handling of trades from GMX_v2"""

import asyncio
import time

import ray
from requests.exceptions import HTTPError

from contract_abi import abi
from handlers.addition_data_handler import handle_position
from handlers.event_handler import handle_event
from handlers.trades_handler import handle_trades
from prisma import Prisma
from web3_manager.proxy import add_case, pick_uri, uri_not_working
from web3_manager.utils import build_web3

providers = [
    "https://arbitrum-one-rpc.publicnode.com",
    "https://arbitrum-one.publicnode.com",
    "https://arb-pokt.nodies.app",
    "https://arbitrum.meowrpc.com",
    "https://open-platform.nodereal.io/c519f6b2fce14790aef78c1693420d0e/arbitrum-nitro/",
]

# Initiating ray for distributed computing
ray.init()

# Initialize Prisma client
prisma = Prisma()


def process_events(all_events, data, w3):
    """
    Processes events and appends trades and positions to data.
    Args:
        events: List of events to process.
        data: List to which trades and positions will be appended.
    """
    for k, event in enumerate(all_events):
        if event["args"]["eventName"] == "PositionFeesCollected":
            trade = handle_event(all_events[k + 1], w3)
            if trade is not None:
                position = handle_position(all_events[k + 1], event, trade["token"])
                data.append([trade, position])
                time.sleep(0.1)  # To avoid hitting rate limits


@ray.remote
def get_trades(i, total):
    """
    Fetches trades for a range of blocks.
    Args:
        i(int): Starting block number for fetching trades.
        total: Total number of blocks to be listen.
    Returns:
        data: A list of trades retrieved from the blockchain.
    """
    data = []
    # Defining the provider URL for connecting to the Arbitrum network
    j = i
    while j < i + total:
        provider_index = pick_uri()
        # Building a Web3 instance
        w3 = build_web3(providers[provider_index])
        # Creating a GMX_V2 contract instance
        contract_abi = abi()
        contract_address = w3.to_checksum_address(
            "0xC8ee91A54287DB53897056e12D9819156D3822Fb"
        )
        contract = w3.eth.contract(abi=contract_abi, address=contract_address)

        while True:
            # Creating a filter to fetch events in the specified block range
            event_filter = contract.events.EventLog1.create_filter(
                fromBlock=j, toBlock=j + 49999
            )
            try:
                # Retrieving all entries from the event filter
                all_events = event_filter.get_all_entries()
                process_events(all_events, data, w3)
                add_case(provider_index, "Success")
                j += 50000
                break
            except ValueError:
                # Wait before retrying
                add_case(provider_index, "Fail")
                time.sleep(1)
            except HTTPError:
                uri_not_working(provider_index)
                break
    return data


async def get_last_updated_block():
    """Getting the last updated block in database"""
    await prisma.connect()
    last_trade = await prisma.trade.find_first(order={"block_number": "desc"})
    last_update = await prisma.block.find_first()
    if last_update is None:
        await prisma.block.create(data={"last_update": 110856764})
        last_update_block = 110856764
    else:
        if last_trade is not None:
            last_update_block = max(last_update.last_update, last_trade.block_number)
            await prisma.block.update_many(
                where={"id": 1}, data={"last_update": last_update_block}
            )
        else:
            last_update_block = 110856764
    await prisma.disconnect()
    return last_update_block


def get_latest_block():
    """Getting the latest block in the arbitrium chain"""
    provider_index = pick_uri()
    w3 = build_web3(providers[provider_index])
    while True:
        try:
            block_number = w3.eth.block_number
            add_case(provider_index, "Success")
            return block_number
        except HTTPError:
            uri_not_working(provider_index)


while True:
    from_block = asyncio.run(get_last_updated_block())
    to_block = get_latest_block()
    total_blocks = to_block - from_block
    # Creating remote tasks for each chunk
    if total_blocks >= 3000000:
        tasks = [
            get_trades.remote(x, 500000)
            for x in range(from_block, from_block + 3000000, 500000)
        ]
        last_block = from_block + 3000000
    else:
        tasks = [
            get_trades.remote(x, int(total_blocks / 6))
            for x in range(from_block, to_block, int(total_blocks / 6))
        ]
        last_block = to_block

    # Executing the remote tasks and gather the results
    trades_combined = ray.get(tasks)

    async def handler(all_trades):
        """Handling each trade data"""
        await handle_trades(all_trades, last_block)

    asyncio.run(handler(trades_combined))
