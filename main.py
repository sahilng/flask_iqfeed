from flask import Flask,render_template, request
import pyiqfeed as iq
import datetime
import time





app = Flask(__name__)

def getStockData(ticker: str, seconds: int):
	"""Get level 1 quotes and trades for ticker for seconds seconds."""

	quote_conn = iq.QuoteConn(name="pyiqfeed-Example-lvl1")
	quote_listener = iq.VerboseQuoteListener("Level 1 Listener")
	quote_conn.add_listener(quote_listener)
	with iq.ConnConnector([quote_conn]) as connector:
		all_fields = sorted(list(iq.QuoteConn.quote_msg_map.keys()))
		quote_conn.select_update_fieldnames(["Bid", "Bid Time", "Ask", "Ask Time"])
		quote_conn.watch(ticker)
		time.sleep(seconds)
		quote_conn.unwatch(ticker)
		quote_conn.remove_listener(quote_listener)

def getOptionData(ticker: str):
	lookup_conn = iq.LookupConn(name="pyiqfeed-Example-Eq-Option-Chain")
	lookup_listener = iq.VerboseIQFeedListener("EqOptionListener")
	lookup_conn.add_listener(lookup_listener)
	with iq.ConnConnector([lookup_conn]) as connector:
		# noinspection PyArgumentEqualDefault
		e_opt = lookup_conn.request_equity_option_chain(
			symbol=ticker,
			opt_type='pc',
			month_codes="".join(iq.LookupConn.call_month_letters + iq.LookupConn.put_month_letters),
			near_months=None,
			include_binary=True,
			filt_type=0, filt_val_1=None, filt_val_2=None)
			#print("Currently trading options for %s" % ticker)
			#print(e_opt)
		lookup_conn.remove_listener(lookup_listener)
	return ticker

#def getFuturesData(ticker: str):

def getTestData(ticker: str):
	return "Ticker: " + ticker


@app.route('/getdata', methods=['GET', 'POST'])
def getData():
	if request.method == 'POST':
	 	ticker = request.form['ticker']
	# 	tickertype = request.form['tickertype']
	# 	if (tickertype == "Stocks"):
	# 		data = ""
	# 	elif (tickertype == "Options"):
	# 		data = getOptionData(ticker)
	# 	elif (tickertype == "Futures"):
	# 		data = ""
	# 	elif (tickertype == "Test"):
	# 		data = getTestData(ticker)
	# 	return data
	return get(ticker)


@app.route('/')
def main():
    	return render_template("main.html")