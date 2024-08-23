"""Module to update in the database"""

from mymath.avg_calc import avg_calc


def pos_settled(trade_data, position_data):
    """
    Returns a dict for a closed position to update in the database.
    Args:
        trade_data: Contains the relavent data of the trade.
        position_details: Contains the relavent data of the trades position so far.
    Return:
        Dict: Relavent information to update in database
    """
    trade_details = trade_data[0]
    additional_details = trade_data[1]
    avg_data = avg_calc(position_data, trade_data)
    if trade_details["token"] == "WBTC":
        decimal = 8
    else:
        decimal = 18
    if trade_details["events"] == "Close":
        ct_decimal = decimal
    else:
        ct_decimal = 6
    pos_settled_data = {
        "id": trade_details["transaction_hash"] + "_" + str(trade_details["log_index"]),
        "link": trade_details["link"],
        "account": trade_details["account"],
        "collateral_token": trade_details["collateral_token"],
        "market_token": additional_details["market_token"],
        "token": trade_details["token"],
        "long_token": trade_details["token"],
        "short_token": "USDC",
        "position_side": trade_details["position_side"],
        "key": "0x" + additional_details["key"],
        "index_token_decimal": decimal,
        "long_token_decimal": decimal,
        "short_token_decimal": 6,
        "index_token_gmx_decimal": 30 - decimal,
        "long_token_gmx_decimal": 30 - decimal,
        "short_token_gmx_decimal": 24,
        "collateral_token_gmx_decimal": 30 - ct_decimal,
        "collateral_token_decimal": ct_decimal,
        "cummulative_size_in_usd": position_data.cum_size,
        "cummulative_collateral": position_data.cum_collateral,
        "size_in_usd": trade_details["size"],
        "size_in_token": trade_details["size"],
        "collateral_in_usd": trade_details["collateral_amount"],
        "max_size": position_data.max_size,
        "max_collateral": position_data.max_collateral,
        "open_block_number": position_data.open_blocknumber,
        "open_block_timestamp": position_data.open_blocktimestamp,
        "block_number": trade_details["block_number"],
        "block_timestamp": trade_details["timestamp"],
        "last_increased_timestamp": position_data.last_increase_timestamp,
        "last_decreased_timestamp": position_data.last_decrease_timestamp,
        "number_of_increase": position_data.number_of_increase,
        "number_of_decrease": position_data.number_of_decrease + 1,
        "last_decreased_index_token_price_min": position_data.last_decreased_index_token_price_min,
        "last_decreased_index_token_price_max": position_data.last_decreased_index_token_price_max,
        "last_increased_index_token_price_min": position_data.last_increased_index_token_price_min,
        "last_increased_index_token_price_max": position_data.last_increased_index_token_price_max,
        "last_decreased_collateral_token_price_min": position_data.last_decreased_collateral_token_price_min,
        "last_decreased_collateral_token_price_max": position_data.last_decreased_collateral_token_price_max,
        "last_increased_collateral_token_price_min": position_data.last_increased_collateral_token_price_min,
        "last_increased_collateral_token_price_max": position_data.last_increased_collateral_token_price_max,
        "average_open_price": trade_details["size_delta"]/additional_details["size_delta_token"],
        "average_close_price": avg_data[1],
        "settled_price": trade_details["price"],
        "is_liquidated": trade_details["events"] == "Liquidated",
        "realised_pnl": position_data.realised_pnl + trade_data[0]["pnl_usd"],
        "roi": (position_data.realised_pnl + trade_data[0]["pnl_usd"])/position_data.max_collateral*100,
        "index_token_price_max": additional_details["it_price_max"],
        "index_token_price_min": additional_details["it_price_min"],
        "collateral_token_price_max": additional_details["ct_price_max"],
        "collateral_token_price_min": additional_details["ct_price_min"],
        "index_token_open_price_min": position_data.index_token_open_price_min,
        "index_token_open_price_max": position_data.index_token_open_price_max,
        "size_updated_at": trade_details["timestamp"],
        "funding_fee_amount": additional_details["funding_fee_amount"],
        "position_fee_amount": additional_details["position_fee_amount"],
        "borrowing_fee_amount": additional_details["borrowing_fee_amount"],
        "ui_fee_amount": additional_details["ui_fee_amount"],
        "trader_discount_amount": additional_details["trader_discount"],
        "total_fee_amount": additional_details["total_fee_amount"],
        "fees_updated_at": trade_details["timestamp"],
        "transaction_hash": trade_details["transaction_hash"],
        "log_index": trade_details["log_index"],
    }
    return pos_settled_data


def pos_open(trade_data):
    """
    Returns a dict for a open position to update in the database.
    Args:
        trade_data: Contains the relavent data of the trade.
    Return:
        Dict: Relavent information to update in database
    """
    pos_unsettled_data = {
        "max_size": trade_data[0]["size"],
        "max_collateral": trade_data[0]["collateral_amount"],
        "cum_size": trade_data[0]["size"],
        "cum_collateral": trade_data[0]["collateral_amount"],
        "open_blocknumber": trade_data[0]["block_number"],
        "open_blocktimestamp": trade_data[0]["timestamp"],
        "last_increase_timestamp": None,
        "last_decrease_timestamp": None,
        "number_of_increase": 1,
        "number_of_decrease": 0,
        "size_of_decrease": None,
        "average_close_price": None,
        "last_decreased_index_token_price_min": None,
        "last_decreased_index_token_price_max": None,
        "last_increased_index_token_price_min": None,
        "last_increased_index_token_price_max": None,
        "last_decreased_collateral_token_price_min": None,
        "last_decreased_collateral_token_price_max": None,
        "last_increased_collateral_token_price_min": None,
        "last_increased_collateral_token_price_max": None,
        "index_token_open_price_min": trade_data[1]["it_price_min"],
        "index_token_open_price_max": trade_data[1]["it_price_max"],
        "link": trade_data[0]["link"],
        "realised_pnl": 0,
    }
    return pos_unsettled_data


def pos_inc(position_data, trade_data):
    """
    Returns a dict for a position increase to update in the database.
    Args:
        trade_data: Contains the relavent data of the trade.
        pos_data: Contains the relavent data of the trades position so far.
    Return:
        Dict: Relavent information to update in database
    """
    pos_unsettled_data = {
        "max_size": max(position_data.max_size, trade_data[0]["size"]),
        "max_collateral": max(
            position_data.max_collateral, trade_data[0]["collateral_amount"]
        ),
        "cum_size": position_data.cum_size + trade_data[0]["size_delta"],
        "cum_collateral": position_data.cum_collateral
        + trade_data[0]["collateral_delta"],
        "last_increase_timestamp": trade_data[0]["timestamp"],
        "number_of_increase": position_data.number_of_increase + 1,
        "last_increased_index_token_price_min": trade_data[1]["it_price_min"],
        "last_increased_index_token_price_max": trade_data[1]["it_price_max"],
        "last_increased_collateral_token_price_min": trade_data[1]["ct_price_min"],
        "last_increased_collateral_token_price_max": trade_data[1]["ct_price_max"],
        "link": trade_data[0]["link"],
    }
    return pos_unsettled_data


def pos_dec(position_data, trade_data):
    """
    Returns a dict for a position decrease to update in the database.
    Args:
        trade_data: Contains the relavent data of the trade.
        pos_data: Contains the relavent data of the trades position so far.
    Return:
        Dict: Relavent information to update in database
    """
    avg_data = avg_calc(position_data, trade_data)
    pos_unsettled_data = {
        "max_size": max(position_data.max_size, trade_data[0]["size"]),
        "max_collateral": max(
            position_data.max_collateral, trade_data[0]["collateral_amount"]
        ),
        "last_decrease_timestamp": trade_data[0]["timestamp"],
        "number_of_decrease": position_data.number_of_decrease + 1,
        "size_of_decrease": avg_data[0],
        "average_close_price": avg_data[1],
        "last_decreased_index_token_price_min": trade_data[1]["it_price_min"],
        "last_decreased_index_token_price_max": trade_data[1]["it_price_max"],
        "last_decreased_collateral_token_price_min": trade_data[1]["ct_price_min"],
        "last_decreased_collateral_token_price_max": trade_data[1]["ct_price_max"],
        "link": trade_data[0]["link"],
        "realised_pnl": position_data.realised_pnl + trade_data[0]["pnl_usd"],
    }
    return pos_unsettled_data
