import json
import yfinance as yf
import pandas as pd
from ta.utils import dropna
from ta.trend import SMAIndicator

# import requests


def lambda_handler(event, context):

    amzn_ticker = yf.Ticker("AMZN")
    amzn_hist = amzn_ticker.history(period="1y")
    amzn_hist.reset_index(inplace=True)
    amzn_hist = amzn_hist[['Open','High','Low','Close','Volume']]

    # drop nulls
    amzn_hist = dropna(amzn_hist)

    # initialize SMA
    indicator_sma = SMAIndicator(amzn_hist["Close"], window=20)
    amzn_hist["SMA"] = indicator_sma.sma_indicator()




    # convert last 5 rows of amzn_hist into string
    amzn_hist_str = amzn_hist.tail().to_string()
    print(amzn_hist_str)



    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": amzn_hist_str,
            # "location": ip.text.replace("\n", "")
        }),
    }

if __name__ == "__main__":
    lambda_handler(None, None)
