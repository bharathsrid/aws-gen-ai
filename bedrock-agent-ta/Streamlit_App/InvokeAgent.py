from boto3.session import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials
import json
import traceback
import os
from requests import request
import base64
import io
import sys

#For this to run on a local machine in VScode, you need to set the AWS_PROFILE environment variable to the name of the profile/credentials you want to use.
#You also need to input your model ID near the bottom of this file.

#check for credentials
#echo $AWS_ACCESS_KEY_ID
#echo $AWS_SECRET_ACCESS_KEY
#echo $AWS_SESSION_TOKEN


#os.environ["AWS_PROFILE"] = "agent-demo"
theRegion = "us-east-1"
os.environ["AWS_REGION"] = theRegion
region = os.environ.get("AWS_REGION")
llm_response = ""

def sigv4_request(
    url,
    method='GET',
    body=None,
    params=None,
    headers=None,
    service='execute-api',
    region=os.environ['AWS_REGION'],
    credentials=Session().get_credentials().get_frozen_credentials()
):
    """Sends an HTTP request signed with SigV4
    Args:
    url: The request URL (e.g. 'https://www.example.com').
    method: The request method (e.g. 'GET', 'POST', 'PUT', 'DELETE'). Defaults to 'GET'.
    body: The request body (e.g. json.dumps({ 'foo': 'bar' })). Defaults to None.
    params: The request query params (e.g. { 'foo': 'bar' }). Defaults to None.
    headers: The request headers (e.g. { 'content-type': 'application/json' }). Defaults to None.
    service: The AWS service name. Defaults to 'execute-api'.
    region: The AWS region id. Defaults to the env var 'AWS_REGION'.
    credentials: The AWS credentials. Defaults to the current boto3 session's credentials.
    Returns:
     The HTTP response
    """

    # sign request
    req = AWSRequest(
        method=method,
        url=url,
        data=body,
        params=params,
        headers=headers
    )
    SigV4Auth(credentials, service, region).add_auth(req)
    req = req.prepare()

    # send request
    return request(
        method=req.method,
        url=req.url,
        headers=req.headers,
        data=req.body
    )


def askQuestion(question, url, endSession=False):
    myobj = {
        "inputText": question,
        "enableTrace": True,
        "endSession": endSession
    }

    # send request
    response = sigv4_request(
        url,
        method='POST',
        service='bedrock',
        headers={
            'content-type': 'application/json',
            'accept': 'application/json',
        },
        region=theRegion,
        body=json.dumps(myobj)
    )

    return decode_response(response)


# def decode_response(response):
#     # Create a StringIO object to capture print statements
#     captured_output = io.StringIO()
#     sys.stdout = captured_output

#     # Your existing logic
#     string = ""
#     for line in response.iter_content():
#         try:
#             string += line.decode(encoding='utf-8')
#         except:
#             continue

#     print("Decoded response", string)
#     split_response = string.split(":message-type")
#     print(f"Split Response: {split_response}")
#     print(f"length of split: {len(split_response)}")

#     for idx in range(len(split_response)):
#         if "bytes" in split_response[idx]:
#             #print(f"Bytes found index {idx}")
#             encoded_last_response = split_response[idx].split("\"")[3]
#             decoded = base64.b64decode(encoded_last_response)
#             final_response = decoded.decode('utf-8')
#             print(final_response)
#         else:
#             print(f"no bytes at index {idx}")
#             print(split_response[idx])

#     last_response = split_response[-1]
#     print(f"Lst Response: {last_response}")
#     if "bytes" in last_response:
#         print("Bytes in last response")
#         encoded_last_response = last_response.split("\"")[3]
#         decoded = base64.b64decode(encoded_last_response)
#         final_response = decoded.decode('utf-8')
#     else:
#         print("no bytes in last response")
#         part1 = string[string.find('finalResponse')+len('finalResponse":'):]
#         part2 = part1[:part1.find('"}')+2]
#         final_response = json.loads(part2)['text']

#     final_response = final_response.replace("\"", "")
#     final_response = final_response.replace("{input:{value:", "")
#     final_response = final_response.replace(",source:null}}", "")
#     llm_response = final_response

#     # Restore original stdout
#     sys.stdout = sys.__stdout__

#     # Get the string from captured output
#     captured_string = captured_output.getvalue()

#     # Return both the captured output and the final response
#     return captured_string, llm_response


def find_rationale_text(split_response_dict, all_rationale, all_text):
    try:
        for key, value in split_response_dict.items():
            if key == "rationale":
                if isinstance(value, dict):
                    all_rationale = all_rationale + value['text'] + "\n"
                else:
                    all_rationale = all_rationale + value + "\n"
            elif key == "text":
                all_text = all_text + value + "\n"
            elif isinstance(value, dict):
                all_rationale, all_text = find_rationale_text(value, all_rationale, all_text)
    except Exception as e:
        print(e)
    return all_rationale, all_text


def decode_response(response):
    # Create a StringIO object to capture print statements
    captured_output = io.StringIO()
    print("about to set stdout")
    sys.stdout = captured_output

    # Your existing logic
    try:
        rationale_string = ""

        string = ""
        for line in response.iter_content():
            try:
                string += line.decode(encoding='utf-8')
            except:
                continue

        print("Decoded response", string)
        split_response = string.split(":message-type")
        all_text = ""
        all_rationale = ""
        for ind_split_response in split_response:
            if "event{" in ind_split_response:
                after_open_braces = ind_split_response.split("event{")[1]
                close_split = after_open_braces.split("}")
                json_string = ''
                for i in range(0, len(close_split)-1):
                    json_string = json_string + close_split[i] + "}"
                json_string = "{" + json_string
                split_response_dict = json.loads(json_string)
                all_rationale, all_text = find_rationale_text(split_response_dict, all_rationale, all_text)
                print("")
                print(split_response_dict)
                print("")


        # print(f"type of json loads split response is {type(json.loads(split_response))}")
        # print(f"Split Response: {split_response}")
        print(f"length of split: {len(split_response)}")

        # # get rationale from orchestration trace
        # for ind_split in split_response:
        #     if "rationale" in ind_split and "orchestrationTrace" in ind_split:
        #         # print(f"in orchestrationTrace rationale and i is {i}")
        #         string_after_rationale = ind_split.split("rationale\":{")[1]
        #         rationale = string_after_rationale.split("\"")[3]
        #         print(f"rationale: {rationale}")
        #         if len(rationale.strip()) > 0:
        #             rationale_string = rationale_string + f"Orchestration rationale is :" + rationale + "\n"

        #     elif "rationale" in ind_split:
        #         # print(f"in rationale and i is {i}")
        #         print(f"ind_split in rationale: {ind_split}")
        #         string_after_rationale = ind_split.split("rationale\":\"")[1]
        #         rationale = string_after_rationale.split("\"")[0]
        #         print(f"rationale: {rationale}")
        #         if len(rationale.strip()) > 0:
        #             rationale_string = rationale_string + f"Rationale  is :" + rationale + "\n"



        for idx in range(len(split_response)):
            if "bytes" in split_response[idx]:
                #print(f"Bytes found index {idx}")
                encoded_last_response = split_response[idx].split("\"")[3]
                decoded = base64.b64decode(encoded_last_response)
                final_response = decoded.decode('utf-8')
                print(final_response)
            else:
                print(f"no bytes at index {idx}")
                print(split_response[idx])

        last_response = split_response[-1]
        print(f"Lst Response: {last_response}")
        if "bytes" in last_response:
            print("Bytes in last response")
            encoded_last_response = last_response.split("\"")[3]
            decoded = base64.b64decode(encoded_last_response)
            final_response = decoded.decode('utf-8')
        else:
            print("no bytes in last response")
            part1 = string[string.find('finalResponse')+len('finalResponse":'):]
            part2 = part1[:part1.find('"}')+2]
            final_response = json.loads(part2)['text']

        final_response = final_response.replace("\"", "")
        final_response = final_response.replace("{input:{value:", "")
        final_response = final_response.replace(",source:null}}", "")
        llm_response = final_response

        # Restore original stdout
        sys.stdout = sys.__stdout__
        print("Restored stdout SUCCESS")
        # Print the captured output
        # print(f'captured output is {captured_output.getvalue()}')
        # Get the string from captured output
        captured_string = captured_output.getvalue()
        # print(f"captured response is {captured_string}")
        # print(f"type of captured response is {type(captured_string)}")

        # print(captured_string)
        print("ENDOF")

        # print(f"type of captured response json loads is {type(json.loads(captured_string))}")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print("Restored stdout in Exception ***")
        print(f"error is *** {e}")
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1].lineno
        print(f"Error occurred on line {line_number}")
        print(f"Response is *** {response}")
        print(f"type Response is *** {type(response)}")
        # Print the captured output
        # print(f'captured output is {captured_output.getvalue()}')
        # Get the string from captured output
        # captured_string = captured_output.getvalue()
        print("EXCEPTION captured string START ==== ")
        # print(f"{captured_string}")
        print("EXCEPTION captured string END ==== ")
        print(f"EXCEPTION full rationale is *** {all_rationale}")
        raise e


    # Return both the captured output and the final response
    print("START OF RATIONALE============")
    print(f"{all_rationale}")
    print("END OF RATIONALE============")

    print("START OF ALL_TEXT============")
    print(f"{all_text}")
    print("END OF ALL_TEXT============")
    # return captured_string, llm_response
    print("START OF FULL TRACE============")
    print(captured_string)
    print("END OF FULL TRACE===========")


    # return captured_string, llm_response
    print("START OF LLM RESPONSE============")
    print(llm_response)
    print("END OF LLM RESPONSE============")
    return all_rationale, all_text, llm_response



def lambda_handler(event, context):

    agentId = "8KCZPQNWJ6" #INPUT YOUR AGENT ID HERE
    agentAliasId = "TB7TCZJSPH" # Hits draft alias, set to a specific alias id for a deployed version
    sessionId = event["sessionId"]
    question = event["question"]
    endSession = False

    print(f"Session: {sessionId} asked question: {question}")

    try:
        if (event["endSession"] == "true"):
            endSession = True
    except:
        endSession = False

    url = f'https://bedrock-agent-runtime.{theRegion}.amazonaws.com/agents/{agentId}/agentAliases/{agentAliasId}/sessions/{sessionId}/text'


    try:
        # response, trace_data = askQuestion(question, url, endSession)
        all_rationale, all_text, llm_response = askQuestion(question, url, endSession)
        print("Before JSON DUMPS")
        print(f"type of llm_response is {type(llm_response)}")
        print(f"type of all_rationale is {type(all_rationale)}")
        print(f"type of all_text is {type(all_text)}")
        return {
            "status_code": 200,
            "body": json.dumps({"response": llm_response, "rationale": all_rationale, "text": all_text})
        }
    except Exception as e:
        return {
            "status_code": 500,
            "body": json.dumps({"error": str(e)})
        }

