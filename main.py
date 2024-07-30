"""Module for listening and handling of trades from GMX_v2"""

import time

import ray

from contract_abi import abi
from event_handler import handle_event
from trades_handler import handle_trades, write_header
from web3_utils import build_web3

# Initiating ray for distributed computing
ray.init()


@ray.remote
def get_trades(i):
    """
    Fetches trades for a range of blocks.
    Args:
        i(int): Starting block number for fetching trades.
    Returns:
        data: A list of trades retrieved from the blockchain.
    """
    # Defining the provider URL for connecting to the Arbitrum network
    provider_url = "https://arbitrum-one-rpc.publicnode.com"

    # Building a Web3 instance
    w3 = build_web3(provider_url)

    # Creating a GMX_V2 contract instance
    contract_abi = abi()
    contract_address = w3.to_checksum_address(
        "0xC8ee91A54287DB53897056e12D9819156D3822Fb"
    )
    contract = w3.eth.contract(abi=contract_abi, address=contract_address)

    data = []

    for j in range(i, i + 3399999, 50000):
        while True:
            # Creating a filter to fetch events in the specified block range
            event_filter = contract.events.EventLog1.create_filter(
                fromBlock=j, toBlock=j + 49999
            )
            try:
                # Retrieving all entries from the event filter
                for event in event_filter.get_all_entries():
                    trade = handle_event(event, w3)
                    if trade is not None:
                        data.append(trade)
                        # Waiting to avoid hitting rate limits
                        time.sleep(0.1)
                # Wait before retrying to avoid hitting rate limits
                time.sleep(40)
                break
            except ValueError:
                # Wait before retrying
                time.sleep(5)
    return data


# Creating remote tasks for each chunk
tasks = [get_trades.remote(x) for x in range(110856764, 130554660, 3400000)]

# Executing the remote tasks and gather the results
all_trades = ray.get(tasks)

write_header()

# Handling each trade data
for trades in all_trades:
    for trade_data in trades:
        handle_trades(trade_data)
