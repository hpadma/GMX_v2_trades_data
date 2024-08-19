"""Module for getting the better performed uri"""

import random
import time

fail = [0, 0, 0, 0, 0]
total = [1, 1, 1, 1, 1]
on_use = [0, 0, 0, 0, 0]
failed_time = [0, 0, 0, 0, 0]


def check_uri():
    """Updates the working condition of the provider uri's."""
    for i in range(5):
        if failed_time[i]:
            if time.time() - failed_time[i] > 600:
                # 0 indicates uri is working
                failed_time[i] = 0


def pick_uri():
    """
    Helps for picking the best performed provider.
    Returns:
        provider_index: Returns the index of the provider uri.
    """
    check_uri()
    # percentage of failure of each provider uri
    pof = [
        (fail[i] / total[i], i)
        for i in range(len(fail))
        if on_use[i] < 2 and failed_time[i] == 0
    ]
    # top 3 best providers
    best_providers = sorted(pof)[:3]
    valid_providers = [best_providers[i][1] for i in range(len(best_providers))]
    # Picking randomly from the top 3 best providers
    if not valid_providers:
        # if there are no valid providers it tries again after sometime
        time.sleep(30)
        return pick_uri()
    provider_index = random.choice(valid_providers)
    on_use[provider_index] += 1
    return provider_index


def add_case(provider_index, event):
    """
    Handles the success and failure cases.
    Args:
        provider_index: Index of the provider.
        event: Describes whether the attempt was Success or failure.
    """
    if event == "Fail":
        fail[provider_index] += 1
    else:
        on_use[provider_index] -= 1
    total[provider_index] += 1


def uri_not_working(provider_index):
    """
    Sets the time at which the provider stopped working.
    Args:
        provider_index: Index of the provider which is not working.
    """
    add_case(provider_index, "Fail")
    on_use[provider_index] -= 1
    failed_time[provider_index] = time.time()
