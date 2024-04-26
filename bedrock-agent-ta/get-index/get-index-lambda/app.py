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
    index_name = index_name.replace("<value>", "").replace("</value>", "")
    print(index_name)
    if api_path=="/get-index":
        if index_name == 'brtIndex':
            print("in brtIndex")
            body = {"stocksList":['MSFT','AAPL','AMZN','NVDA','META','GOOG','NFLX','ADBE','QCOM','CSCO']}
        # if lower case index name is nasdaq or ndq the symbols are
        elif index_name.lower() == 'nasdaq' or  index_name.lower() == 'ndq':
            body = {"stocksList":["MSFT","AAPL","NVDA","AMZN","META","AVGO","GOOGL","GOOG","COST","TSLA","NFLX","AMD","PEP","LIN","ADBE","CSCO","QCOM","TMUS","INTU","AMAT","CMCSA","TXN","INTC","AMGN","ISRG","MU","HON","LRCX","BKNG","VRTX","ADP","REGN","SBUX","ADI","KLAC","PANW","MDLZ","SNPS","GILD","CDNS","ASML","PDD","MELI","MAR","CRWD","ABNB","CSX","PYPL","CTAS","ORLY","PCAR","CEG","MRVL","NXPI","ROP","MNST","WDAY","CPRT","DXCM","DASH","FTNT","ADSK","ODFL","MCHP","ROST","PAYX","KHC","AEP","KDP","IDXX","LULU","FAST","MRNA","AZN","GEHC","DDOG","TTD","CHTR","CSGP","FANG","EXC","CTSH","EA","BKR","CDW","TEAM","VRSK","CCEP","XEL","ANSS","BIIB","ON","DLTR","GFS","ZS","MDB","TTWO","W","D","ILMN","WBA","SIRI"]}
        elif index_name.lower() == 'nifty' or  index_name.lower() == 'nft' or index_name.lower() == 'nifty 50':
            body = {"stocksList":["ADANIENT.NS","ADANIPORTS.NS","APOLLOHOSP.NS","ASIANPAINT.NS","AXISBANK.NS","BAJAJ-AUTO.NS","BAJFINANCE.NS","BAJAJFINSV.NS","BPCL.NS","BHARTIARTL.NS","BRITANNIA.NS","CIPLA.NS","COALINDIA.NS","DIVISLAB.NS","DRREDDY.NS","EICHERMOT.NS","GRASIM.NS","HCLTECH.NS","HDFCLIFE.NS","HEROMOTOCO.NS","HINDALCO.NS","HINDUNILVR.NS","ICICIBANK.NS","ITC.NS","INDUSINDBK.NS","INFY.NS","JSWSTEEL.NS","KOTAKBANK.NS","LTIM.NS","LT.NS","M&M.NS","MARUTI.NS","NTPC.NS","NESTLEIND.NS","ONGC.NS","POWERGRID.NS","RELIANCE.NS","SBILIFE.NS","SBIN.NS","SUNPHARMA.NS","TCS.NS","TATACONSUM.NS","TATAMOTORS.NS","TATASTEEL.NS","TECHM.NS","TITAN.NS","ULTRACEMCO.NS","WIPRO.NS"]}
        elif index_name.lower() == 'ftse100' or  index_name.lower() == 'ftse' or  index_name.lower() == 'ftse 100':
            body = {"stocksList":["III.L","ADM.L","AAF.L","AAL.L","ANTO.L","AHT.L","ABF.L","AZN.L","AUTO.L","AV.L","BME.L","BA.L","BARC.L","BDEV.L","BEZ.L","BKG.L","BP.L","BATS.L","BNZL.L","BRBY.L","CNA.L","CCH.L","CPG.L","CTEC.L","CRDA.L","DCC.L","DGE.L","DPLM.L","EZJ.L","ENT.L","EXPN.L","FCIT.L","FLTR.L","FRAS.L","FRES.L","GLEN.L","GSK.L","HLN.L","HLMA.L","HIK.L","HWDN.L","HSBA.L","IMI.L","IMB.L","INF.L","IHG.L","ICG.L","IAG.L","ITRK.L","JD.L","KGF.L","LAND.L","LGEN.L","LLOY.L","LSEG.L","MNG.L","MKS.L","MRO.L","MNDI.L","NG.L","NWG.L","NXT.L","OCDO.L","PSON.L","PSH.L","PSN.L","PHNX.L","PRU.L","RKT.L","REL.L","RTO.L","RMV.L","RIO.L","RR.L","RS1.L","SGE.L","SBRY.L","SDR.L","SMT.L","SGRO.L","SVT.L","SHEL.L","SN.L","SMDS.L","SMIN.L","SKG.L","SPX.L","SSE.L","STJ.L","STAN.L","TW.L","TSCO.L","ULVR.L","UTG.L","UU.L","VOD.L","WEIR.L","WTB.L","WPP.L"]}        
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
