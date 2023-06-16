# kynance
tools for automating options trading

# to-do
- [x] factor out parser
- [x] factor out rh in strategy interface
- [x] validate user input
- [x] scrape optionslam for all it's historical data (where to put it)?
- [ ] calculate future earning's statistics on my own
- [x] calculate the probability of profit
- [ ] dockerize
- [ ] automatically write to a journal
     - [ ] how do i match opening a position with closing a position?
- [ ] figure out what to do about getting rate-limited by the rh api
- [x] what to do about DECRYPTION_FAILED_OR_BAD_RECORD_MAC errors due to @timeout
     - switched to the y_finance --data-source which removed the need to "timeout" when the right strike price couldn't be found using the rh api
- [x] convert download_all.py into a cmd
- [x] logging
     - using a metaclass MethodLoggerMeta
     - various wrapper functions for static, member and class methods
- [ ] ~~optimize hitting yahoo finance, robinhood api.~~
- [ ] makefile
- [ ] ~~use rh to get tickers of interest, download all of them at once with yf.download~~
- [ ] add straddle_price, straddle_strikes to ticker_report.py and many_ticker_report.py
- [x] dynamically calculate the max days in max_mean
- [x] dynamically calculate the max days in max_mediam
- [x] show the ratio in the profit probability % for ticker_report.py
- [x] show the ratio in the protity probability % for the many_ticker_report.py
- [ ] provide a link to robinhood in the ticker column for many_ticker_report.py
- [ ] provide a link to robinhood in the ticker column for ticker_report.py
- [ ] fix index 0 is out of bounds for axis 0 with size 0 errors from yfinance
- [ ] write some tests
- [ ] schedule on a cron-tab
- [ ] send notifications via email and text
- [ ] how to deploy to a raspberry pi?
- [ ] scrape historical options data from https://www.cboe.com/us/options/market_statistics/historical_data/
    - [ ] use that data to backfill straddle_predicted_move and profit_probability