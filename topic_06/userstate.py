"""
This module implements a class to keep track of the user state.
"""

class UserState:
    """
    This class will be used to help keep track of the state of users as
    blocks are accepted onto the blockchain.
    """
    def __init__(self, balance : int, nonce : int):
        """
        Initialize the user state.

        Parameters:
            balance (int): The (on-chain) balance of the user.
            nonce (int): The most recently used nonce of the user.
        """
        self.balance = balance
        self.nonce = nonce
