from strategies.statistics import ClosePercent, \
    MaxMeanMovement, MaxMedianMovement, \
    StraddlePredictedMovement, ProfitProbability, Statistics


class StatisticFactory(object):
    def __init__(self, days, client_username, client_password, client_mfa):
        self.client_username = client_username
        self.client_password = client_password
        self.client_mfa = client_mfa
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
                    stat.name, file,
                    self.client_username,
                    self.client_password,
                    self.client_mfa,
                    ticker)
            case Statistics.profit_probability:
                return ProfitProbability(
                    stat.name, file,
                    self.client_username,
                    self.client_password,
                    self.client_mfa,
                    ticker
                )
