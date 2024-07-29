"""Module for creating a Web3 instance"""

from web3 import Web3


def build_web3(provider_url):
    """
    Creates a Web3 instance using the given HTTP provider URL.
    Args:
        provider_url (str): The URL of the provider service.
    Returns:
        w3: A Web3 instance connected to the node specified by provider_url.
    """
    w3 = Web3(Web3.HTTPProvider(provider_url))
    return w3
