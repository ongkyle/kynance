from strategies.statistics import ClosePercent, \
    MaxMeanMovement, MaxMedianMovement, \
    StraddlePredictedMovement, ProfitProbability, \
    Statistics, Statistic

from clients.client import OptionsClient


class StatisticFactory(object):
    def __init__(self, days: int):
        self.days = days

    def create(self, stat: Statistics, file: str, ticker: str, client: OptionsClient) -> Statistic:
        match stat:
            case Statistics.close_percent:
                return ClosePercent(
                    stat_name=stat.name,
                    csv_file=file,
                    days=self.days
                )
            case Statistics.max_mean:
                return MaxMeanMovement(
                    stat_name=stat.name,
                    csv_file=file,
                    days=self.days
                )
            case Statistics.max_median:
                return MaxMedianMovement(
                    stat_name=stat.name,
                    csv_file=file,
                    days=self.days
                )
            case Statistics.straddle_predicted_move:
                return StraddlePredictedMovement(
                    stat_name=stat.name,
                    csv_file=file,
                    client=client,
                    ticker=ticker,
                    days=self.days
                )
            case Statistics.profit_probability:
                return ProfitProbability(
                    stat_name=stat.name,
                    csv_file=file,
                    client=client,
                    ticker=ticker,
                    days=self.days
                )
