# Mapping token addresses to their token names
token_hash = {'0x47c031236e19d024b42f8AE6780E44A573170703': 'WBTC',
              '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336': 'WETH',
              '0x7f1fa204bb700853D36994DA19F830b6Ad18455C': 'LINK',
              '0xc7Abb2C5f3BF3CEB389dF0Eecd6120D451170B50': 'UNI'}


def pos_increase(event, timestamp, eventname):
    """
    Process a PositionIncrease event and returns relevant data.
    Args:
        event: event data.
        timestamp: timestamp of the block containing the event.
        eventname: type of the event either 'Open' or 'Increase'.
    Returns:
        trade_event: Relavant information from the event data.
    """
    account = event['args']['eventData']['addressItems']['items'][0]['value']
    collateral_token = event['args']['eventData']['addressItems']['items'][2]['value']
    token = token_hash[event['args']['eventData']['addressItems']['items'][1]['value']]
    collateral_amount = event['args']['eventData']['uintItems']['items'][2]['value']
    collateral_delta = event['args']['eventData']['intItems']['items'][0]['value']
    size = event['args']['eventData']['uintItems']['items'][0]['value']
    size_delta = event['args']['eventData']['uintItems']['items'][12]['value']
    position_side = 'LONG' if event['args']['eventData']['boolItems']['items'][0]['value'] else 'SHORT'
    link = event['args']['eventData']['bytes32Items']['items'][1]['value'].hex()
    price = event['args']['eventData']['uintItems']['items'][11]['value']
    block_number = event['blockNumber']
    transaction_hash = event['transactionHash'].hex()
    log_index = event['logIndex']
    pnl_usd = 0

    trade_event = [account, eventname, collateral_token, token, collateral_amount,
                   collateral_delta, size, size_delta, position_side, link, price, block_number,
                   timestamp,transaction_hash,log_index,pnl_usd]
    return trade_event


def pos_decrease(event, timestamp, eventname):
    """
    Process a PositionDecrease event and returns relevant data.
    Args:
        event: event data.
        timestamp: timestamp of the block containing the event.
        eventname: type of the event either 'Close' or 'Decrease'.
    Returns:
        trade_event: Relavant information from the event data.
    """
    account = event['args']['eventData']['addressItems']['items'][0]['value']
    collateral_token = event['args']['eventData']['addressItems']['items'][2]['value']
    token = token_hash[event['args']['eventData']['addressItems']['items'][1]['value']]
    collateral_amount = event['args']['eventData']['uintItems']['items'][2]['value']
    collateral_delta = event['args']['eventData']['uintItems']['items'][14]['value']
    size = event['args']['eventData']['uintItems']['items'][0]['value']
    size_delta = event['args']['eventData']['uintItems']['items'][12]['value']
    position_side = 'LONG' if event['args']['eventData']['boolItems']['items'][0]['value'] else 'SHORT'
    link = event['args']['eventData']['bytes32Items']['items'][1]['value'].hex()
    price = event['args']['eventData']['uintItems']['items'][11]['value']
    block_number = event['blockNumber']
    transaction_hash = event['transactionHash'].hex()
    log_index = event['logIndex']
    pnl_usd = event['args']['eventData']['intItems']['items'][1]['value']

    trade_event = [account, eventname, collateral_token, token, collateral_amount,
                   collateral_delta, size, size_delta, position_side, link, price, block_number,
                   timestamp,transaction_hash,log_index,pnl_usd]
    return trade_event


def liquidated(event, timestamp):
    """
    Process a Liquidated event and returns relevant data.
    Args:
        event: event data.
        timestamp: timestamp of the block containing the event.
    Returns:
        trade_event: Relavant information from the event data.
    """
    account = event['args']['eventData']['addressItems']['items'][0]['value']
    collateral_token = event['args']['eventData']['addressItems']['items'][2]['value']
    token = token_hash[event['args']['eventData']['addressItems']['items'][1]['value']]
    collateral_amount = event['args']['eventData']['uintItems']['items'][2]['value']
    collateral_delta = event['args']['eventData']['uintItems']['items'][14]['value']
    size = event['args']['eventData']['uintItems']['items'][0]['value']
    size_delta = event['args']['eventData']['uintItems']['items'][12]['value']
    position_side = 'LONG' if event['args']['eventData']['boolItems']['items'][0]['value'] else 'SHORT'
    link = event['args']['eventData']['bytes32Items']['items'][1]['value'].hex()
    price = event['args']['eventData']['uintItems']['items'][11]['value']
    block_number = event['blockNumber']
    transaction_hash = event['transactionHash'].hex()
    log_index = event['logIndex']
    pnl_usd = event['args']['eventData']['intItems']['items'][1]['value']

    trade_event = [account, 'Liquidated', collateral_token, token, collateral_amount,
                   collateral_delta, size, size_delta, position_side, link, price, block_number,
                   timestamp,transaction_hash,log_index,pnl_usd]
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
    #Checking if its a liquidated event
    if event['args']['msgSender'] == '0xB665B6dBB45ceAf3b126cec98aDB1E611b6a6aea':
        if event['args']['eventName'] == 'PositionDecrease':
            if event['args']['eventData']['addressItems']['items'][1]['value'] in token_hash:
                return liquidated(event, w3.eth.get_block(event['blockNumber']).timestamp)

    else:
        if event['args']['eventName'] == 'PositionIncrease':
            if event['args']['eventData']['addressItems']['items'][1]['value'] in token_hash:
                timestamp = w3.eth.get_block(event['blockNumber']).timestamp
                # If size is equal to size_delta then event type is Open.
                if event['args']['eventData']['uintItems']['items'][0]['value'] == event['args']['eventData']['uintItems']['items'][12]['value']:
                    return pos_increase(event, timestamp, 'Open')
                return pos_increase(event, timestamp, 'Increase')

        elif event['args']['eventName'] == 'PositionDecrease':
            if event['args']['eventData']['addressItems']['items'][1]['value'] in token_hash:
                timestamp = w3.eth.get_block(event['blockNumber']).timestamp
                # If size = 0 then event type is Close
                if event['args']['eventData']['uintItems']['items'][0]['value'] == 0:
                    return pos_decrease(event, timestamp, 'Close')
                return pos_decrease(event, timestamp, 'Decrease')
