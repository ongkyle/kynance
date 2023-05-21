'''
1. --backfill w/ rh.get_all_option_positions()
    - write journal.csv to disk
    - read into memory dataframe
    - calculate statistics
    - write back to disk
2. --update continuously add w/ rh.get_open_option_positions()
    - read into memory dataframe
    - calculate statistics
    - append to journal.csv
3. --view
    - read journal.csv into memory dataframe
    - pretty print the dataframe

csv file
chain_symbol,expiration_date,strike_price,option_type,side,order_created_at,direction,order_quantity,order_type,opening_strategy,closing_strategy,price,processed_quantity
Trade Entry	Symbol	Strategy	Underlying Open Price	Strikes traded	# contracts traded	Profit Probability	Implied Volatility	Premium	% max profit % max loss	Trade Exit	Underlying Close Price	Premium Close	Profit	Profit Margin	Defined Risk?	Net
'''
import os.path

from pandas import DataFrame

from cmds.cmd import Cmd
from robinhood.robinhood import Robinhood


class Journal(object):
    def __init__(self, abs_file_path, client_username, client_password, client_mfa):
        self.abs_file_path = abs_file_path
        self.username = client_username
        self.password = client_password
        self.mfa = client_mfa
        self.client = Robinhood(username=self.username, password=self.password, mfa_code=self.mfa)


class JournalUpdate(Cmd, Journal):
    def execute(self):
        print("Hello, d")


class JournalBackfill(Cmd, Journal):
    def execute(self):
        self.export_option_trade_history()
        df = self.get_dataframe()

    def export_option_trade_history(self):
        dir = os.path.dirname(self.abs_file_path)
        basename = os.path.basename(self.abs_file_path)
        self.client.export_option_trade_history(dir, basename)

    def get_dataframe(self):
        return DataFrame(self.abs_file_path)