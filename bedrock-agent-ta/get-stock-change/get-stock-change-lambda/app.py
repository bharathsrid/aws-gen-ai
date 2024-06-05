import json
import pandas as pd
import boto3
import os
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
    print(f"stock lis is {stock_list_input}")
    print(f"type of stock list is {type(stock_list_input)}")
    cleaned_stock_list_input_string = stock_list_input.replace('[','').replace(']','').replace('"','').replace(', ',',')
    cleaned_stock_list_input_string = cleaned_stock_list_input_string.replace("<value>", "").replace("</value>", "")
    stock_list = cleaned_stock_list_input_string.split(",")
    
    print(stock_list)
    print(type(stock_list))
    no_of_days = int(params['noOfDays'].replace("<value>", "").replace("</value>", ""))

    # download csv file from a s3 bucket into /tmp
    s3 = boto3.resource('s3')
    bucket = os.getenv('S3_BUCKET') 
    s3.Bucket(bucket).download_file('stock_hist/stock_data_1y.csv', '/tmp/stock_data_1y.csv')
    stock_1y_df = pd.read_csv('/tmp/stock_data_1y.csv')
    # convert the Date column in dataframe from string to datetime date
    stock_1y_df['Date'] = pd.to_datetime(stock_1y_df['Date'])

    percent_change_dict = {}


    if api_path=="/get-stock-change":
        print("in stock change")

        for stock in stock_list:
            print(stock)
            stock_df = stock_1y_df[stock_1y_df['Symbol'] == stock]
            # filter stock df to retain only last 1 week data using the Date column as reference
            stock_1w_df = stock_df[stock_df['Date'] > stock_df['Date'].max() - pd.Timedelta(days=no_of_days)]
            try:
                print(stock_1w_df.head(1))
                print(stock_1w_df.tail(1))
                first_close = stock_1w_df['Close'].iloc[0]
                last_close = stock_1w_df['Close'].iloc[-1]
                pct_change = ((last_close/first_close) - 1)*100
                percent_change_dict[stock] = pct_change
            except Exception as e:
                print(f"errored getting percentage with error {e}")
                percent_change_dict[stock] = "NA"
            
        # convert the dictionary into json string
        body = percent_change_dict





        # stock_1w_df['Date'] = pd.to_datetime(stock_1w_df['Date'], infer_datetime_format=True)
        # print(stock_1w_df['Date'].dtype)
        # # reconvert datetime of Date column to string in dd-MMM-YYYY format
        # stock_1w_df['Date'] = stock_1w_df['Date'].dt.strftime('%d-%b-%Y')
        # body = stock_1w_df.to_json(orient='records')

    else:
        body = list({"{} is not a valid api, try another one.".format(api_path)})


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
