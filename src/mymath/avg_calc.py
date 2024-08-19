"""Module for calculating average open price and average close price"""


def avg_calc(position_data, trade_data):
    """
    Calculates average open and close prices.
    Args:
        position_data: Contains the previous data of the position taken.
        trade_data: Contains data of present trade data.
    Returns:
        Updated size and average
    """
    if trade_data[0]["events"] == "Increase":
        cumulative = (
            position_data.size_of_increase * position_data.average_open_price
            + trade_data[0]["price"] * trade_data[0]["size"]
        )
        position_data.size_of_increase += trade_data[0]["size"]
        avg = cumulative / position_data.size_of_increase
        return position_data.size_of_increase, avg

    if not position_data.size_of_decrease:
        return [trade_data[0]["size"], trade_data[0]["price"]]

    cumulative = (
        position_data.size_of_decrease * position_data.average_close_price
        + trade_data[0]["price"] * trade_data[0]["size"]
    )
    position_data.size_of_decrease += trade_data[0]["size"]
    avg = cumulative / position_data.size_of_decrease
    return position_data.size_of_decrease, avg
