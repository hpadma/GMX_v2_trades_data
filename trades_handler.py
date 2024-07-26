import csv


# Stores the position count of all links
position_count = {}
# Stores the latest position count of links for each tokens
token_position = {'WBTC': {},
                  'WETH': {},
                  'LINK': {},
                  'UNI': {}}


def write_header():
    """
    Writes the header row to the CSV file when initiating the CSV File.
    """
    with open('trades.csv', 'w', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ['account', 'events', 'collateral_token', 'token', 'collateral_amount',
                  'collateral_delta', 'size', 'size_delta', 'position_side', 'link', 'price',
                  'block_number', 'timestamp', 'transaction_hash', 'log_index', 'pnl_usd']
        writer.writerow(header)


def write(trade_data):
    """
    Appends a row of trade to the CSV file.
    Args:
        trade_data: List containing trade information to be written to the CSV file.
    """
    with open('trades.csv', 'a', newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(trade_data)


def counter(trade_data):
    '''
    Updates and returns the postion link count for each account.
    Args:
        trade_data: List containing trade information.
    Returns:
        int: Position count of link 
    '''
    events = trade_data[1]
    token = trade_data[3]
    position_link = trade_data[9]

    #For the event Open increase the position link count else return present count
    if events == 'Open':
        # Increase the count if link already exist else intiatiate it with 1
        if position_link in position_count:
            position_count[position_link] += 1
            token_position[token][position_link] = position_count[position_link]
        else:
            position_count[position_link] = 1
            token_position[token][position_link] = position_count[position_link]
    else:
        token_position[token][position_link] = position_count[position_link]
    return position_count[position_link]


def handle_trades(trade_data):
    """
    Updates the position link and writes the trade data to the CSV file.
    Args:
        trade_data: List containing trade information.
    """
    # Get the updated position link count
    link_counter = counter(trade_data)
    # Change the format of link and update in CSV file
    trade_data[9] = 'PositionLink_'+str(link_counter)+'_0x'+str(trade_data[9])
    write(trade_data)
