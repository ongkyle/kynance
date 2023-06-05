# kynance
tools for automating options trading

# to-do
[x] factor out parser
[x] factor out rh in strategy interface
[x] validate user input
[x] scrape optionslam for all it's historical data (where to put it)?
[ ] calculate future earning's statistics on my own
[x] calculate the probability of profit
[ ] dockerize
[ ] automatically write to a journal
    - [ ] how do i match opening a position with closing a position?
[ ] figure out what to do about getting rate-limited by the rh api
[x] what to do about DECRYPTION_FAILED_OR_BAD_RECORD_MAC errors due to @timeout
    - switched to the y_finance --data-source which removed the need to "timeout" when the right strike price couldn't be found using the rh api
[x] convert download_all.py into a cmd
[ ] logging
[ ] optimize hitting yahoo finance, robinhood api.
[ ] makefile
[ ] use rh to get tickers of interest, download all of them at once with yf.download