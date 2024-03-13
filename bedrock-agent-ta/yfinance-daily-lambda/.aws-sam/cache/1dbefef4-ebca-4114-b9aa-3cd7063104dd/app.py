import json
import yfinance as yf
import pandas as pd
from ta.utils import dropna
from ta.trend import SMAIndicator
import boto3
from botocore.exceptions import ClientError


# import requests


def lambda_handler(event, context):

    symbol_list = ['MSFT','AAPL','AMZN','NVDA','META','GOOG','NFLX','ADBE','QCOM','CSCO']

    # initiate an empty data frame for 1 year stock data
    stock_hist_all = pd.DataFrame()
    for symbol in symbol_list:
        stock_ticker = yf.Ticker(symbol)
        stock_hist = stock_ticker.history(period="1y")
        stock_hist.reset_index(inplace=True)
        stock_hist["Symbol"] = symbol
        stock_hist = stock_hist[['Symbol','Date','Open','High','Low','Close','Volume']]

        # drop nulls
        stock_hist = dropna(stock_hist)

        # # initialize SMA
        # indicator_sma = SMAIndicator(stock_hist["Close"], window=20)
        # stock_hist["SMA"] = indicator_sma.sma_indicator()

    

        #add the value of this stock to the data frame stock_hist_all
        stock_hist_all = pd.concat([stock_hist_all, stock_hist])


     # convert last 5 rows of stock_hist into string
    stock_hist_str = stock_hist.tail().to_string()
    print(stock_hist_str)   


    # WRITE THE DATAFRAME TO A CSV FILE IN s3
    # reset index
    # stock_hist_all.reset_index(inplace=True)
    stock_hist_all.to_csv('/tmp/stock_data_1y.csv',index=False) 
    bucket = 'bharsrid-bedrock-agent-yf-demo'
    key = 'stock_hist/stock_data_1y.csv'
    s3 = boto3.client('s3')

    try:
        s3.upload_file('/tmp/stock_data_1y.csv', bucket, key)
    except ClientError as e:
        logging.error(e)
        return False
    return True





    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": stock_hist_str,
            # "location": ip.text.replace("\n", "")
        }),
    }

if __name__ == "__main__":
    lambda_handler(None, None)
