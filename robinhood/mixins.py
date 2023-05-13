import datetime


class OptionsMixin(object):
    def find_options_by_expiration_and_strike(self, symbols, expiration_date, strike_price, info=None):
        return self.client.find_options_by_expiration_and_strike(
            inputSymbols=symbols,
            expirationDate=expiration_date,
            strikePrice=strike_price,
            info=info)

    def find_option_mark_price(self, symbols, expiration_date, strike_price):
        options = self.find_options_by_expiration_and_strike(symbols, expiration_date, strike_price)
        mark_price = [
            option.get("mark_price", None) for option in options
        ]
        return mark_price

    def find_options_mark_price_by_strike(self, inputSymbols, strikePrice, optionType=None, info=None):
        options = self.client.find_options_by_strike(inputSymbols, strikePrice, optionType, info)
        mark_price = [
            option.get("mark_price", None) for option in options
        ]
        return mark_price

    def get_earnings_report(self, symbols):
        earnings = self.client.get_earnings(symbol=symbols, info="report")
        earnings = [earning for earning in earnings if earning != None]
        return [report["date"] for report in earnings]

    def get_closest(self, needle, haystack):
        haystack.sort()
        for potential in haystack:
            if potential >= needle:
                return potential

    def convert_to_dates(self, arr):
        return [
            datetime.date.fromisoformat(date) for date
            in arr
        ]

    def get_next_earnings_date(self, symbol):
        earnings = self.get_earnings_report(symbol)
        earnings_dates = self.convert_to_dates(earnings)
        return self.get_closest(datetime.date.today(), earnings_dates)

    def get_options_chain(self, symbol):
        return self.client.get_chains(symbol=symbol, info="expiration_dates")

    def get_option_chain_dates(self, symbol):
        options_chain = self.get_options_chain(symbol)
        return self.convert_to_dates(options_chain)

    def get_chain_just_after_earnings(self, symbol):
        expiration_dates = self.get_option_chain_dates(symbol)
        earnings_date = self.get_next_earnings_date(symbol)
        return self.get_closest(earnings_date, expiration_dates)

    def get_latest_price(self, symbol):
        return float(self.client.get_latest_price(inputSymbols=symbol)[0])

    def convert_to_float(self, arr):
        return [
            float(ele) for ele in arr
        ]

    def calculate_straddle_predicted_movement(self, straddle_price, latest_price):
        return 100 * (straddle_price / latest_price)

    def get_closest_option_mark_price(self, symbol, expiration_date, latest_price):
        strike_price = latest_price
        option_prices = []
        while len(option_prices) == 0:
            option_prices = self.find_option_mark_price(
                symbol,
                expiration_date=expiration_date,
                strike_price=strike_price,
            )
            strike_price += 0.5
            strike_price = round(strike_price, 1)
        return option_prices

    def get_straddle_predicted_movement(self, symbol):
        post_earnings_expiry_chain = self.get_chain_just_after_earnings(symbol)
        latest_price = self.get_latest_price(symbol)
        option_prices = self.get_closest_option_mark_price(symbol, str(post_earnings_expiry_chain), round(latest_price))
        option_prices = self.convert_to_float(option_prices)
        straddle_price = sum(option_prices)
        straddle_predicted_movement = self.calculate_straddle_predicted_movement(straddle_price, latest_price)
        straddle_predicted_movement = round(straddle_predicted_movement, 2)
        return straddle_predicted_movement
