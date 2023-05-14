import pandas as pd
from enum import Enum
from dataframe import Dataframe
from robinhood.robinhood import *
from strategies.strategy import Strategy


class Statistics(Enum):
    close_percent = 0
    max_mean = 1
    max_median = 2
    straddle_predicted_move = 3


class Statistic(Dataframe):
    def __init__(self, stat_name, csv_file, **kwargs):
        super().__init__(csv_file=csv_file)
        self.stat_name = stat_name


class RhStatistic(Statistic):
    def __init__(self, stat_name, csv_file, username, password, mfa_code, ticker, **kwargs):
        super().__init__(stat_name=stat_name, csv_file=csv_file)
        self.ticker = ticker
        self.rh = Robinhood(username=username, password=password, mfa_code=mfa_code)


class ClosePercent(Statistic, Strategy):

    def execute(self):
        return self.calculate_close_percent()

    @property
    def title(self):
        return self.stat_name

    def calculate_close_percent(self):
        self.df[self.stat_name] = self.df["Close Price"] - self.df["Price Before"]
        self.df[self.stat_name] = self.df[self.stat_name] / self.df["Price Before"]
        self.df[self.stat_name] = self.df[self.stat_name] * 100
        return self.title, self.df[self.stat_name]


class MaxMeanMovement(Statistic, Strategy):
    def __init__(self, stat_name, csv_file, days):
        super().__init__(stat_name=stat_name, csv_file=csv_file)
        self.stat_name = stat_name
        self.days = days

    def execute(self):
        return self.calculate_historical_max_mean_movement()

    @property
    def title(self):
        return f"{self.days} day {self.stat_name} %"

    def calculate_historical_max_mean_movement(self):
        historical_max_means = []
        num_earnings = self.df.shape[0]
        num_earnings_with_days_observations = num_earnings - self.days

        for i in range(0, num_earnings_with_days_observations):
            window = self.df["Max Move"][i:self.days + i].abs()
            historical_max_means.append(window.mean())

        return self.title, pd.Series(historical_max_means,
                                     index=[idx for idx in range(num_earnings - 1, self.days - 1, -1)])


class MaxMedianMovement(Statistic, Strategy):
    def __init__(self, stat_name, csv_file, days):
        super().__init__(stat_name=stat_name, csv_file=csv_file)
        self.stat_name = stat_name
        self.days = days

    def execute(self):
        return self.calculate_historical_max_median_movement()

    @property
    def title(self):
        return f"{self.days} day {self.stat_name} %"

    def calculate_historical_max_median_movement(self):
        historical_max_medians = []
        num_earnings = self.df.shape[0]
        num_earnings_with_days_observations = num_earnings - self.days

        for i in range(0, num_earnings_with_days_observations):
            window = self.df["Max Move"][i:self.days + i].abs()
            historical_max_medians.append(window.median())

        return self.title, pd.Series(historical_max_medians,
                                     index=[idx for idx in range(num_earnings - 1, self.days - 1, -1)])


class StraddlePredictedMovement(RhStatistic, Strategy):

    def execute(self):
        straddle_predicted_movement = self.rh.get_straddle_predicted_movement(self.ticker)
        return self.title, pd.Series(straddle_predicted_movement, index=[self.df.shape[0] - 1])

    @property
    def title(self):
        return f"{self.stat_name} %"
