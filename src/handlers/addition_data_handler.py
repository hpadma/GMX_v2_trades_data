"""Module which handles the fee and price of the tokens for a sspecific trades"""


def pos_data(event, fees, token):
    """
    Returns the additional data like fees of the trade.
    Args:
        event(Attribute Dictionary): event details of the trade.
        fees(Attribute Dictionary):  fees details of the trade.
        token: Token traded.
    Return:
        Dict: Relevant additional information from the event data.
    """
    data = event["args"]["eventData"]
    fee = fees["args"]["eventData"]

    address_items = data["addressItems"]["items"]
    uint_items = data["uintItems"]["items"]
    bytes32_items = data["bytes32Items"]["items"]
    fee_uint = fee["uintItems"]["items"]

    if token == "WBTC":
        decimal_factor = 1e8
        it_decimal = 1e22
    else:
        decimal_factor = 1e18
        it_decimal = 1e12

    if event["args"]["msgSender"] == "0xB665B6dBB45ceAf3b126cec98aDB1E611b6a6aea":
        ct_decimal = 1e6 / 1e30
    else:
        ct_decimal = decimal_factor / 1e30

    additional_data = {
        "market_token": address_items[1]["value"],
        "key": bytes32_items[1]["value"].hex(),
        "funding_fee_amount": fee_uint[8]["value"] / decimal_factor,
        "position_fee_amount": fee_uint[24]["value"] / decimal_factor,
        "borrowing_fee_amount": fee_uint[15]["value"] / decimal_factor,
        "ui_fee_amount": fee_uint[27]["value"] / decimal_factor,
        "total_fee_amount": fee_uint[25]["value"] / decimal_factor,
        "trader_discount": fee_uint[6]["value"] / decimal_factor,
        "it_price_max": uint_items[8]["value"] / it_decimal,
        "it_price_min": uint_items[9]["value"] / it_decimal,
        "ct_price_max": uint_items[10]["value"] * ct_decimal,
        "ct_price_min": uint_items[11]["value"] * ct_decimal,
    }

    return additional_data


def handle_position(event, fees, token):
    """Returns the additional data like fees and price of tokens"""
    return pos_data(event, fees, token)
