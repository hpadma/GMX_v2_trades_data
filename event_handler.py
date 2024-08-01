"""Module for filtering the events"""

# Mapping token addresses to their token names
token_hash = {
    "0x47c031236e19d024b42f8AE6780E44A573170703": "WBTC",
    "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336": "WETH",
    "0x7f1fa204bb700853D36994DA19F830b6Ad18455C": "LINK",
    "0xc7Abb2C5f3BF3CEB389dF0Eecd6120D451170B50": "UNI",
}


def pos_increase(event, timestamp, eventname):
    """
    Process a PositionIncrease event and return relevant data.
    Args:
        event: Event data.
        timestamp: Timestamp of the block containing the event.
        eventname: Type of the event, either 'Open' or 'Increase'.
    Returns:
        list: Relevant information from the event data.
    """
    # Extracting event data fields into a single dictionary
    print(f"inc, {event['blockNumber']}")
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    int_items = data["intItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]

    trade_event = {
        "account": address_items[0]["value"],
        "events": eventname,
        "collateral_token": address_items[2]["value"],
        "token": token_hash[address_items[1]["value"]],
        "collateral_amount": uint_items[2]["value"] / 1e6,
        "collateral_delta": int_items[0]["value"] / 1e6,
        "size": uint_items[0]["value"] / 1e30,
        "size_delta": uint_items[12]["value"] / 1e30,
        "position_side": "LONG" if bool_items[0]["value"] else "SHORT",
        "link": bytes32_items[1]["value"].hex(),
        "price": uint_items[11]["value"] / 1e30,
        "block_number": event["blockNumber"],
        "timestamp": timestamp,
        "transaction_hash": event["transactionHash"].hex(),
        "log_index": event["logIndex"],
        "pnl_usd": 0,
    }

    return trade_event


def pos_decrease(event, timestamp, eventname):
    """
    Process a PositionDecrease event and return relevant data.
    Args:
        event: Event data.
        timestamp: Timestamp of the block containing the event.
        eventname: Type of the event, either 'Close' or 'Decrease'.
    Returns:
        list: Relevant information from the event data.
    """
    # Extracting event data fields into a single dictionary
    print(f"dec, {event['blockNumber']}")
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]
    int_items = data["intItems"]["items"]

    trade_event = {
        "account": address_items[0]["value"],
        "events": eventname,
        "collateral_token": address_items[2]["value"],
        "token": token_hash[address_items[1]["value"]],
        "collateral_amount": uint_items[2]["value"] / 1e6,
        "collateral_delta": uint_items[14]["value"] / 1e6,
        "size": uint_items[0]["value"] / 1e30,
        "size_delta": uint_items[12]["value"] / 1e30,
        "position_side": "LONG" if bool_items[0]["value"] else "SHORT",
        "link": bytes32_items[1]["value"].hex(),
        "price": uint_items[11]["value"] / 1e30,
        "block_number": event["blockNumber"],
        "timestamp": timestamp,
        "transaction_hash": event["transactionHash"].hex(),
        "log_index": event["logIndex"],
        "pnl_usd": int_items[1]["value"] / 1e30,
    }

    return trade_event


def liquidated(event, timestamp):
    """
    Process a Liquidated event and return relevant data.
    Args:
        event: Event data.
        timestamp: Timestamp of the block containing the event.
    Returns:
        list: Relevant information from the event data.
    """
    # Extracting event data fields into a single dictionary
    print(f"liq, {event['blockNumber']}")
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]
    int_items = data["intItems"]["items"]

    trade_event = {
        "account": address_items[0]["value"],
        "events": "Liquidated",
        "collateral_token": address_items[2]["value"],
        "token": token_hash[address_items[1]["value"]],
        "collateral_amount": uint_items[2]["value"] / 1e6,
        "collateral_delta": uint_items[14]["value"] / 1e6,
        "size": uint_items[0]["value"] / 1e30,
        "size_delta": uint_items[12]["value"] / 1e30,
        "position_side": "LONG" if bool_items[0]["value"] else "SHORT",
        "link": bytes32_items[1]["value"].hex(),
        "price": uint_items[11]["value"] / 1e30,
        "block_number": event["blockNumber"],
        "timestamp": timestamp,
        "transaction_hash": event["transactionHash"].hex(),
        "log_index": event["logIndex"],
        "pnl_usd": int_items[1]["value"] / 1e30,
    }

    return trade_event


def handle_event(event, w3):
    """
    Handles the event and returns the data of relavant event.
    Args:
        event: The event data.
        w3: The Web3 instance.
    Returns:
        list: Information extracted from event data if the event matches the criteria, else None.
    """
    # Checking if its a liquidated event
    if event["args"]["msgSender"] == "0xB665B6dBB45ceAf3b126cec98aDB1E611b6a6aea":
        if event["args"]["eventName"] == "PositionDecrease":
            if (
                event["args"]["eventData"]["addressItems"]["items"][1]["value"]
                in token_hash
            ):
                return liquidated(
                    event, w3.eth.get_block(event["blockNumber"]).timestamp
                )

    else:
        if event["args"]["eventName"] == "PositionIncrease":
            if (
                event["args"]["eventData"]["addressItems"]["items"][1]["value"]
                in token_hash
            ):
                timestamp = w3.eth.get_block(event["blockNumber"]).timestamp
                # If size is equal to size_delta then event type is Open.
                if (
                    event["args"]["eventData"]["uintItems"]["items"][0]["value"]
                    == event["args"]["eventData"]["uintItems"]["items"][12]["value"]
                ):
                    return pos_increase(event, timestamp, "Open")
                return pos_increase(event, timestamp, "Increase")

        elif event["args"]["eventName"] == "PositionDecrease":
            if (
                event["args"]["eventData"]["addressItems"]["items"][1]["value"]
                in token_hash
            ):
                timestamp = w3.eth.get_block(event["blockNumber"]).timestamp
                # If size = 0 then event type is Close
                if event["args"]["eventData"]["uintItems"]["items"][0]["value"] == 0:
                    return pos_decrease(event, timestamp, "Close")
                return pos_decrease(event, timestamp, "Decrease")

    return None
