import json
import pandas as pd
import boto3
from ta.utils import dropna
from ta.trend import SMAIndicator, EMAIndicator

# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """

    # try:
    #     ip = requests.get("http://checkip.amazonaws.com/")
    # except requests.RequestException as e:
    #     # Send some context about this error to Lambda Logs
    #     print(e)

    #     raise e

    print(event)
    responses = []
    api_path = event['apiPath']
    params = dict((param['name'], param['value']) for param in event['parameters'])


    stock_list_input = params['stockList']
    cleaned_stock_list_input_string = stock_list_input.replace('[','').replace(']','').replace('"','') 
    stock_list = cleaned_stock_list_input_string.split(", ")
    
    print(stock_list)
    print(type(stock_list))
    print(len(stock_list))
    no_of_days = int(params['noOfDays'])
    tech_analysis = params['techAnalysis']

    # download csv file from a s3 bucket into /tmp
    s3 = boto3.resource('s3')
    s3.Bucket('bharsrid-bedrock-agent-yf-demo').download_file('stock_hist/stock_data_1y.csv', '/tmp/stock_data_1y.csv')
    stock_1y_df = pd.read_csv('/tmp/stock_data_1y.csv')
    # convert the Date column in dataframe from string to datetime date
    stock_1y_df['Date'] = pd.to_datetime(stock_1y_df['Date'])

    stock_ta_list = []


    if api_path=="/get-stock-ta":
        print("in stock change")

        for stock in stock_list:
            tmp_ta_dict={}
            tmp_ta_dict["stock"]=stock
            print(stock)
            stock_df = stock_1y_df[stock_1y_df['Symbol'] == stock]
            # # initialize SMA
            if tech_analysis == "SMA":
                indicator_ta = SMAIndicator(stock_df["Close"], window=no_of_days)
                stock_df["TA"] = indicator_ta.sma_indicator()
                print(stock_df.tail(5))
                print(stock_df['Close'])
                print(type(stock_df['Close']))
                # assign the last row close to stock_close variable
                stock_close = stock_df['Close'].iloc[-1]
                stock_ta = stock_df['TA'].iloc[-1]
                tmp_ta_dict["close"] = stock_close
                tmp_ta_dict["ta"] = stock_ta
                # add tmp_ta_dict to stock_ta_list
                stock_ta_list.append(tmp_ta_dict)
            elif tech_analysis == "EMA":
                indicator_ta = EMAIndicator(stock_df["Close"], window=no_of_days)
                stock_df["TA"] = indicator_ta.ema_indicator()
                print(stock_df.tail(5))
                print(stock_df['Close'])
                print(type(stock_df['Close']))
                stock_close = stock_df['Close'].iloc[-1]
                stock_ta = stock_df['TA'].iloc[-1]
                tmp_ta_dict["close"] = stock_close
                tmp_ta_dict["ta"] = stock_ta
                stock_ta_list.append(tmp_ta_dict)
            else:
                body = {"{} is not a valid technical analysis, try another one.".format(tech_analysis)}  


        # convert the dictionary into json string
        body = stock_ta_list


    else:
        body = {"{} is not a valid api, try another one.".format(api_path)}


    response_body = {
        'application/json': {
            'body': json.dumps(body)
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    responses.append(action_response)

    api_response = {
        'messageVersion': '1.0',
        'response': action_response}

    return api_response
