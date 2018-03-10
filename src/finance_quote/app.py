"""
Entry point to the library.
This main class is called from the cli and it is the
entry point for the users of the library.
"""
import logging
from typing import List


class App:
    """ The main entry point to the F::Q library """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.modules = ['alphavantage']

    def alphavantage(self, symbols):
        """ example using av as provider """
        # TODO invoke av module for fetching price
        # from .modules import av
        if isinstance(symbols, str):
            # handle single symbol
            pass
        elif isinstance(symbols, List):
            # handle list of symbols
            pass
        else:
            raise ValueError("Invalid argument sent")
