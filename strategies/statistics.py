import pandas as pd
from enum import Enum

from dataframe import Dataframe
from strategies.strategy import Strategy
from log.metaclass import MethodLoggerMeta

__metaclass__ = MethodLoggerMeta


class Statistics(Enum):
    close_percent = 0
    max_mean = 1
    max_median = 2
    straddle_predicted_move = 3
    profit_probability = 4


class Statistic(Dataframe, metaclass=MethodLoggerMeta):
    def __init__(self, stat_name, csv_file, days, *args, **kwargs):
        super().__init__(csv_file=csv_file, *args, **kwargs)
        self.stat_name = stat_name
        self.days = days

    def num_days_to_calculate(self) -> int:
        num_earnings = self.num_earnings
        if self.days >= num_earnings:
            return num_earnings
        return num_earnings - self.days

    def get_window_length(self) -> int:
        if self.days >= self.num_earnings:
            return self.num_earnings
        return self.days

    def get_index(self) -> list[int]:
        idx = [idx for idx in range(self.num_earnings - 1, self.days - 1, -1)]
        if self.days >= self.num_earnings:
            idx = [idx for idx in range(self.num_earnings - 1, -1, -1)]
        return idx

    @property
    def num_earnings(self) -> int:
        return self.df.shape[0]


class RhStatistic(Statistic):
    def __init__(self, stat_name, csv_file, client, ticker, *args, **kwargs):
        super().__init__(stat_name=stat_name, csv_file=csv_file, *args, **kwargs)
        self.ticker = ticker
        self.client = client


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
    def __init__(self, stat_name, csv_file, days, *args, **kwargs):
        super().__init__(stat_name=stat_name, csv_file=csv_file, days=days, *args, **kwargs)
        self.stat_name = stat_name
        self.days = days

    def execute(self):
        return self.calculate_historical_max_mean_movement()

    @property
    def title(self):
        return f"n day {self.stat_name} %"

    def calculate_historical_max_mean_movement(self):
        historical_max_means = []
        days_to_calculate = self.num_days_to_calculate()

        for i in range(0, days_to_calculate):
            window = self.df["Max Move"].iloc[i:days_to_calculate + i].abs()
            historical_max_means.append(window.mean())

        idx = self.get_index()
        return self.title, pd.Series(historical_max_means, index=idx)


class MaxMedianMovement(Statistic, Strategy):
    def __init__(self, stat_name, csv_file, days, *args, **kwargs):
        super().__init__(stat_name=stat_name, csv_file=csv_file, days=days, *args, **kwargs)
        self.stat_name = stat_name
        self.days = days

    def execute(self):
        return self.calculate_historical_max_median_movement()

    @property
    def title(self):
        return f"n day {self.stat_name} %"

    def calculate_historical_max_median_movement(self):
        historical_max_medians = []
        days_to_calculate = self.num_days_to_calculate()

        for i in range(0, days_to_calculate):
            window = self.df["Max Move"].iloc[i:days_to_calculate + i].abs()
            historical_max_medians.append(window.median())

        idx = self.get_index()
        return self.title, pd.Series(historical_max_medians, index=idx)


class StraddlePredictedMovement(RhStatistic, Strategy):

    def execute(self):
        straddle_predicted_movement = self.client.get_straddle_predicted_movement()
        return self.title, pd.Series(straddle_predicted_movement, index=[self.df.shape[0] - 1])

    @property
    def title(self):
        return f"{self.stat_name} %"


class ProfitProbability(RhStatistic, Strategy):

    def execute(self):
        return self.title, self.calculate_profit_probability()

    def calculate_profit_probability(self):
        window_length = self.get_window_length()
        if window_length <= 0:
            return pd.Series(0)
        straddle_predicted_movement = self.get_straddle_predicted_movement()
        if straddle_predicted_movement.isnull().all():
            profit_probability = pd.Series(None, index=[self.df.shape[0] - 1])
            return profit_probability
        max_moves = self.get_max_moves()
        comparison = straddle_predicted_movement.values < max_moves.abs().values
        probability = (comparison.sum() / window_length) * 100
        probability = round(probability, 2)
        probability = str(f"{probability}% ({comparison.sum()}/{window_length})")
        return pd.Series(probability, index=[self.df.shape[0] - 1])

    def get_straddle_predicted_movement(self):
        window_length = self.get_window_length()
        straddle_predicted_movement = self.client.get_straddle_predicted_movement()
        straddle_predicted_movement = pd.Series(straddle_predicted_movement for _ in range(window_length))
        return straddle_predicted_movement

    def get_max_moves(self):
        return self.df["Max Move"].iloc[0:self.get_window_length()]

    @property
    def title(self):
        return f"{self.stat_name} %"
