import json

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
    index_name = params['indexName'] 
    print(index_name)
    if api_path=="/get-index":
        if index_name == 'brtIndex':
            print("in brtIndex")
            body = {"stocksList":['MSFT','AAPL','AMZN','NVDA','META','GOOG','NFLX','ADBE','QCOM','CSCO']}
        else:
            body = list({"{} is not a valid Index the tool supports, try another index ".format(event['inputText'])})

    else:
        body = list({"{} is not a valid api, try another one.".format(api_path)})

    print(body)
    print(type(body))
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

    return {
        "statusCode": 200,
        "body": json.dumps({
            "brtIndex": index_list,
            # "location": ip.text.replace("\n", "")
        }),
    }
