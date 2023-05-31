from strategies.statistics import ClosePercent, \
    MaxMeanMovement, MaxMedianMovement, \
    StraddlePredictedMovement, ProfitProbability, Statistics


class StatisticFactory(object):
    def __init__(self, days, client):
        self.client = client
        self.days = days

    def create(self, stat, file, ticker):
        match stat:
            case Statistics.close_percent:
                return ClosePercent(stat.name, file)
            case Statistics.max_mean:
                return MaxMeanMovement(stat.name, file, self.days)
            case Statistics.max_median:
                return MaxMedianMovement(stat.name, file, self.days)
            case Statistics.straddle_predicted_move:
                return StraddlePredictedMovement(
                    stat.name,
                    file,
                    self.client,
                    ticker)
            case Statistics.profit_probability:
                return ProfitProbability(
                    stat.name,
                    file,
                    self.client,
                    ticker
                )
