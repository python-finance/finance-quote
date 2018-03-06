"""
CLI interface to F::Q
"""
import logging

import click
import click_log

from .app import App

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

@click.group()
@click_log.simple_verbosity_option(logger)
def cli():
    """ entry point """
    pass

@click.command()
def alphavantage():
    """ test """
    app = App()
    app.logger = logger
    # do nothing

cli.add_command(alphavantage)
