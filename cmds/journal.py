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

GroupBy ("chain_symbol", "opening_strategy", "order_created_at") will result in groups with only one executed strategy
assumptions
- no two orders can occur at the same time

GroupBy("chain_symbol", "closing_strategy")

for each idx, group in group_by_opening_strategy:
    chain_symbol, opening_strategy, order_created_at = idx[0], idx[1], idx[2]
    closing_strategy = group_by_close.get_group((chain_symbol, opening_strategy))
    underlying_open_price = ??
    profit_probability = calculate_profit_probability()
    implied_vol = get_implied_vol(symbol, strikes_traded, group["option_type"]) ??
    max_profit_% = --max-profit
    max_loss_% = get_max_loss(--max-profit)
    underlying_close_price = ??
    profit = calculate_profit(premium_open, premium_close) * num_contracts_traded
    profit_margin = calculate_profit_margin(premium_open, premium_close)
    defined_risk = defined_risk_strategies[opening_strategy]
    net = calculate_net_profit(profit)


'''
import math
import os.path
from enum import Enum

import pandas as pd
from pandas import DataFrame

from cmds.cmd import Cmd
from clients import Robinhood


class OptionStrategy(Enum):
    long_call = 0
    long_call_spread = 1
    long_put_spread = 2
    long_put = 3
    short_call = 4
    short_call_spread = 5
    short_put_spread = 6
    straddle = 7
    custom = 8
    iron_condor = 9
    strangle = 10


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
        # self.export_option_trade_history()
        df = self.get_dataframe()
        grouped_by_opening = df.groupby(["chain_symbol", "opening_strategy", "order_created_at"])
        grouped_by_closing = df.groupby(["chain_symbol", "closing_strategy"])
        for idx, open_group in grouped_by_opening:
            chain_symbol, opening_strategy, order_created_at = idx[0], idx[1], idx[2]
            try:
                close_group = grouped_by_closing.get_group((chain_symbol, opening_strategy))
            except KeyError as err:
                print(err)
            strikes_traded_open = " ".join(str(val) for val in open_group["strike_price"].values)
            strikes_traded_close = " ".join(str(val) for val in open_group["strike_price"].values)
            num_contracts_traded = int(open_group["order_quantity"].sum())
            # premium_open = " ".join(str(val) for val in group["price"].values)
            trade_exit_date = close_group["order_created_at"].values
            premium_close = close_group["price"].values
            premium_open = open_group["price"].values
            strategy = opening_strategy if not opening_strategy == "nan" else close_group
            # profit = self.calculate_profit(premium_open, premium_close, OptionStrategy(strategy))
            print(f"{chain_symbol}, enter date: {order_created_at}, exit_date: {trade_exit_date}, {opening_strategy}, "
                  f"# contracts: {num_contracts_traded}, strikes open: {strikes_traded_open}, "
                  f"strikes close: {strikes_traded_close}, premium open: {premium_open}, premium close: {premium_close}")

    def calculate_profit(self, open, close, num_contracts, strategy):
        match strategy:
            case OptionStrategy.long_put_spread:
                return self.calculate_long_put_spread_profit(open, close, num_contracts)
            case OptionStrategy.long_call_spread:
                return self.calculate_long_call_spread_profit(open, close, num_contracts)
            case OptionStrategy.custom:
                return self.calculate_custom_profit(open, close, num_contracts)
            case OptionStrategy.strangle:
                return self.calculate_strangle_profit(open, close, num_contracts)
            case OptionStrategy.long_call:
                return self.calculate_long_call_profit(open, close, num_contracts)
            case OptionStrategy.long_put:
                return self.calculate_long_put_profit(open, close, num_contracts)
            case OptionStrategy.iron_condor:
                return self.calculate_iron_condor_profit(open, close, num_contracts)
            case OptionStrategy.short_call_spread:
                return self.calculate_short_call_spread_profit(open, close, num_contracts)
            case OptionStrategy.short_put_spread:
                return self.calculate_short_put_spread_profit(open, close, num_contracts)
            case OptionStrategy.straddle:
                return self.calculate_straddle_profit(open, close, num_contracts)

    def calculate_long_put_spread_profit(self, open, close, num_contracts):
        return close - open

    def calculate_long_call_spread_profit(self, open, close, num_contracts):
        return close - open

    def calculate_custom_profit(self, open, close, num_contracts):
        print(f"Calculating profit for custom strategies is not support.")

    def calculate_strangle_profit(self, open, close, num_contracts):
        pass

    def export_option_trade_history(self):
        dir = os.path.dirname(self.abs_file_path)
        basename = os.path.basename(self.abs_file_path)
        self.client.export_option_trade_history(dir, basename)

    def get_dataframe(self):
        return pd.read_csv(self.abs_file_path)
