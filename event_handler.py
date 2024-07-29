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
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    int_items = data["intItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]

    trade_event = [
        address_items[0]["value"],  # account
        eventname,  # eventname
        address_items[2]["value"],  # collateral_token
        token_hash[address_items[1]["value"]],  # token
        uint_items[2]["value"],  # collateral_amount
        int_items[0]["value"],  # collateral_delta
        uint_items[0]["value"],  # size
        uint_items[12]["value"],  # size_delta
        "LONG" if bool_items[0]["value"] else "SHORT",  # position_side
        bytes32_items[1]["value"].hex(),  # link
        uint_items[11]["value"],  # price
        event["blockNumber"],  # block_number
        timestamp,  # timestamp
        event["transactionHash"].hex(),  # transaction_hash
        event["logIndex"],  # log_index
        0,  # pnl_usd
    ]

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
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]
    int_items = data["intItems"]["items"]

    trade_event = [
        address_items[0]["value"],  # account
        eventname,  # eventname
        address_items[2]["value"],  # collateral_token
        token_hash[address_items[1]["value"]],  # token
        uint_items[2]["value"],  # collateral_amount
        uint_items[14]["value"],  # collateral_delta
        uint_items[0]["value"],  # size
        uint_items[12]["value"],  # size_delta
        "LONG" if bool_items[0]["value"] else "SHORT",  # position_side
        bytes32_items[1]["value"].hex(),  # link
        uint_items[11]["value"],  # price
        event["blockNumber"],  # block_number
        timestamp,  # timestamp
        event["transactionHash"].hex(),  # transaction_hash
        event["logIndex"],  # log_index
        int_items[1]["value"],  # pnl_usd
    ]

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
    data = event["args"]["eventData"]

    # Simplified data extraction
    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    bool_items = data["boolItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]
    int_items = data["intItems"]["items"]

    trade_event = [
        address_items[0]["value"],  # account
        "Liquidated",  # eventname
        address_items[2]["value"],  # collateral_token
        token_hash[address_items[1]["value"]],  # token
        uint_items[2]["value"],  # collateral_amount
        uint_items[14]["value"],  # collateral_delta
        uint_items[0]["value"],  # size
        uint_items[12]["value"],  # size_delta
        "LONG" if bool_items[0]["value"] else "SHORT",  # position_side
        bytes32_items[1]["value"].hex(),  # link
        uint_items[11]["value"],  # price
        event["blockNumber"],  # block_number
        timestamp,  # timestamp
        event["transactionHash"].hex(),  # transaction_hash
        event["logIndex"],  # log_index
        int_items[1]["value"],  # pnl_usd
    ]

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
