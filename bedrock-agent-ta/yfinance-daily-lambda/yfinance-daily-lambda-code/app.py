import json
import yfinance as yf
import pandas as pd
from ta.utils import dropna
from ta.trend import SMAIndicator
import boto3
from botocore.exceptions import ClientError


# import requests


def lambda_handler(event, context):

    symbol_list = ["MSFT","AAPL","NVDA","AMZN","META","AVGO","GOOGL","GOOG","COST","TSLA","NFLX","AMD","PEP","LIN","ADBE","CSCO","QCOM","TMUS","INTU","AMAT","CMCSA","TXN","INTC","AMGN","ISRG","MU","HON","LRCX","BKNG","VRTX","ADP","REGN","SBUX","ADI","KLAC","PANW","MDLZ","SNPS","GILD","CDNS","ASML","PDD","MELI","MAR","CRWD","ABNB","CSX","PYPL","CTAS","ORLY","PCAR","CEG","MRVL","NXPI","ROP","MNST","WDAY","CPRT","DXCM","DASH","FTNT","ADSK","ODFL","MCHP","ROST","PAYX","KHC","AEP","KDP","IDXX","LULU","FAST","MRNA","AZN","GEHC","DDOG","TTD","CHTR","CSGP","FANG","EXC","CTSH","EA","BKR","CDW","TEAM","VRSK","CCEP","XEL","ANSS","BIIB","ON","DLTR","GFS","ZS","MDB","TTWO","W","D","ILMN","WBA","SIRI","III.L","ADM.L","AAF.L","AAL.L","ANTO.L","AHT.L","ABF.L","AZN.L","AUTO.L","BME.L","BA.L","BARC.L","BDEV.L","BEZ.L","BKG.L","BP.L","BATS.L","BNZL.L","BRBY.L","CNA.L","CCH.L","CPG.L","CTEC.L","CRDA.L","DCC.L","DGE.L","DPLM.L","EZJ.L","ENT.L","EXPN.L","FCIT.L","FLTR.L","FRAS.L","FRES.L","GLEN.L","GSK.L","HLN.L","HLMA.L","HIK.L","HWDN.L","HSBA.L","IMI.L","IMB.L","INF.L","IHG.L","ICG.L","IAG.L","ITRK.L","JD.L","KGF.L","LAND.L","LGEN.L","LLOY.L","LSEG.L","MNG.L","MKS.L","MRO.L","MNDI.L","NG.L","NWG.L","NXT.L","OCDO.L","PSON.L","PSH.L","PSN.L","PHNX.L","PRU.L","RKT.L","REL.L","RTO.L","RMV.L","RIO.L","RR.L","RS1.L","SGE.L","SBRY.L","SDR.L","SMT.L","SGRO.L","SVT.L","SHEL.L","SN.L","SMDS.L","SMIN.L","SKG.L","SPX.L","SSE.L","STJ.L","STAN.L","TW.L","TSCO.L","ULVR.L","UTG.L","UU.L","VOD.L","WEIR.L","WTB.L","WPP.L","ADANIENT.NS","ADANIPORTS.NS","APOLLOHOSP.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HCLTECH.NS","HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS","HINDUNILVR.NS","ICICIBANK.NS","ITC.NS","INDUSINDBK.NS","INFY.NS","JSWSTEEL.NS","KOTAKBANK.NS","LTIM.NS","LT.NS","M&M.NS","MARUTI.NS","NTPC.NS","NESTLEIND.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS","SBILIFE.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS","TATACONSUM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS"]

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
