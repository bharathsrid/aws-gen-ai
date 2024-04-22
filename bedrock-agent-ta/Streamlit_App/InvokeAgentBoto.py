import boto3
import random
import json

def find_rationale_text(split_response_dict,all_rationale="",all_text=""):
    try:
        for key, value in split_response_dict.items():
            if key == "rationale":
                if isinstance(value, dict):
                    all_rationale = all_rationale + value['text'] + "\n"
                elif value.strip():
                    all_rationale = "Rationale : " + all_rationale + value + "\n"
            elif key == "text":
                all_text = "Text : " + all_text + value + "\n"
            elif isinstance(value, dict):
                all_rationale, all_text = find_rationale_text(value, all_rationale, all_text)
    except Exception as e:
        print("IN FIND RATIONALE TEXT EXCEPTIOPN")
        print(e)
    return all_rationale, all_text


def bedrock_invoke_agent(input,sessionId,enableTrace=True,endSession=False):
    print(f"BEDROCK INVOKED Session id is {sessionId}")
    print(f"Input is {input}")
    print(f"endsession is {endSession}")
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    response = client.invoke_agent(
        agentAliasId='QOFTKHRFU6',
        agentId='8KCZPQNWJ6',
        enableTrace=True,
        endSession=False,
        inputText=input,
        sessionId=sessionId

    )
    # print(response)
    response_text = ""
    rationale = ""
    full_text = ""
    for event in response['completion']:
        if 'chunk' in event:
            # This event contains the response text
            try:
                response_text = json.loads(event['chunk']['bytes'].decode('utf-8'))
                # print("RESPONSE START======")
                # print(response_text)
            except json.decoder.JSONDecodeError as jsde:
                print("Not a valid Json, so directly reading as string")
                response_text = event['chunk']['bytes'].decode('utf-8')
                # print(event["chunk"])

        elif 'trace' in event:  
            # This event contains trace information
            trace = event['trace']['trace']
            parse_rationale, parse_full_text = find_rationale_text(trace)
            rationale = rationale + parse_rationale
            full_text = full_text + parse_full_text
            print("TRACE START =======")
            print(trace)
            print("TRACE END =======")

        else:
            print("NOT CHUNK OR TRACE")

    print("Returning from Bedrock with the following")
    print(f"RESPONSE TEXT IS {response_text}")
    print(f"RATIONALE IS {rationale}")
    print(f"FULL TEXT IS {full_text}")

    return response_text, rationale, full_text

