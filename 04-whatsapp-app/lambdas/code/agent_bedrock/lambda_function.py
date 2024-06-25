#####################################################
## This function queries anthropic.claude-3-sonnet ##
#####################################################

import json
import boto3
import os
import time
import base64
import sys

bedrock_agent_client = boto3.client("bedrock-agent-runtime")
agent_id = os.environ.get('ENV_AGENT_ID')
agent_alias_id = os.environ.get('ENV_ALIAS_ID')
whatsapp_out_lambda = os.environ.get('WHATSAPP_OUT')

from utils import whats_reply


def invoke_agent(agent_id, agent_alias_id, session_id, prompt):
    """
    Sends a prompt for the agent to process and respond to.

    :param agent_id: The unique identifier of the agent to use.
    :param agent_alias_id: The alias of the agent to use.
    :param session_id: The unique identifier of the session. Use the same value across requests
                        to continue the same conversation.
    :param prompt: The prompt that you want Claude to complete.
    :return: Inference response from the model.
    """
    try:
        # Note: The execution time depends on the foundation model, complexity of the agent,
        # and the length of the prompt. In some cases, it can take up to a minute or more to
        # generate a response.
        response = bedrock_agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
        )
        print("response: ",response)

        completion = ""

        for event in response.get("completion"):
            chunk = event["chunk"]
            completion = completion + chunk["bytes"].decode()

    except:
        print(f"Couldn't invoke agent.")
        raise

    return completion

def lambda_handler(event, context):
    print (event)

    prompt = event['whats_message']
    print('REQUEST RECEIVED:', event)
    print('REQUEST CONTEXT:', context)
    print("PROMPT: ",prompt)

    try:
        whats_token = event['whats_token']
        messages_id = event['messages_id']
        phone = event['phone']
        phone_id = event['phone_id']

        completion = invoke_agent(agent_id, agent_alias_id, phone.replace("+",""), prompt)
        
        print(completion) 

        whats_reply(whatsapp_out_lambda,phone, whats_token, phone_id, f"{completion}", messages_id)
        
        return({"body":completion})   
    
    except Exception as error: 
        print('FAILED!', error)
        return({"body":"Cuek! I dont know"})

    

