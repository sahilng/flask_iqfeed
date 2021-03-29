from flask import Flask,render_template, request
import pyiqfeed as iq
import datetime
import time
import numpy as np
 

app = Flask(__name__)

def getQuoteData(ticker: str):
	"""Get level 1 quotes and trades for ticker for seconds seconds."""
	fundamentals = ""
	quote_conn = iq.QuoteConn(name="pyiqfeed-Example-lvl1")
	quote_listener = iq.VerboseQuoteListener("Level 1 Listener")
	quote_conn.add_listener(quote_listener)
	with iq.ConnConnector([quote_conn]) as connector:
		all_fields = sorted(list(iq.QuoteConn.quote_msg_map.keys()))
		quote_conn.select_update_fieldnames(["Bid", "Bid Time", "Ask", "Ask Time"])
		quote_conn.watch(ticker)
		t_end = time.time() + 5*60
		while time.time() < t_end:
			fundamentals = quote_conn.fundamentals
			summary = quote_conn.summary
			if (fundamentals != "" and summary != ""):
				break
		quote_conn.unwatch(ticker)
		quote_conn.remove_listener(quote_listener)
		if (len(summary) > 0):
			summary = summary[0]
	if (len(summary) > 0):
		return fundamentals, summary[0]
	else:
		return ""


def getStockData(ticker: str):
	fundamentals, summary = getQuoteData(ticker)
	return "Summary: " + len(summary[0])


def getOptionData(ticker: str):
	toreturn = ""
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
		for i in e_opt['c'][:10]:
			fundamentals, summary = getQuoteData(i)
			toreturn = toreturn + str(summary)

	return toreturn

def getFuturesData(ticker: str):
	lookup_conn = iq.LookupConn(name="pyiqfeed-Example-Futures-Chain")
	lookup_listener = iq.VerboseIQFeedListener("FuturesChainLookupListener")
	lookup_conn.add_listener(lookup_listener)
	with iq.ConnConnector([lookup_conn]) as connector:
		f_syms = lookup_conn.request_futures_chain(
			symbol=ticker,
			month_codes="".join(iq.LookupConn.futures_month_letters),
			years="67",
			near_months=None,
			timeout=None)
		print("Futures symbols with underlying %s" % ticker)
		print(f_syms)
		lookup_conn.remove_listener(lookup_listener)

def getTestData(ticker: str, tickertype: str):
	return "Ticker: " + ticker + "<br>" + "Ticker type: " + tickertype


@app.route('/getdata', methods=['GET', 'POST'])
def getData():
	if request.method == 'POST':
	 	ticker = request.form['ticker'].upper()
	 	tickertype = request.form['tickertype']

	 	if (tickertype == "Stocks"):
	 		data = getStockData(ticker)
	 		return data
	 	elif (tickertype == "Options"):
	 		data = getOptionData(ticker)
	 		return data
	 	elif (tickertype == "Futures"):
	 		data = ""
	 	elif (tickertype == "Test"):
	 		data = getTestData(ticker)
	 	return data


@app.route('/')
def main():
    	return render_template("main.html")