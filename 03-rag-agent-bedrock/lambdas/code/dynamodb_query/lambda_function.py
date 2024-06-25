#################################################
## This function is to query a dynamoDB table ###
#################################################

import json
from boto3.dynamodb.conditions import Key
import boto3
import botocore.exceptions
import os
import re

dynamodb_resource=boto3.resource('dynamodb')

table_name = os.environ.get('TABLE_NAME')
key_name = os.environ.get('ENV_KEY_NAME')

table = dynamodb_resource.Table(table_name)

def db_query(key,table,keyvalue):
    response = table.query(
        KeyConditionExpression=Key(key).eq(keyvalue)
    )
    print(response)
    return response

def lambda_handler(event, context):
    print(event)
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    item_value = {}

    for n in parameters:
        print(n)
        item = n["name"]
        item_value[item] = n["value"]
        
    print(item_value)
        
    #item_value = json.loads(item)
    item_value[key_name] = item_value[key_name].replace("+","")
    
    '''Handle Lambda event from AWS'''
    # Setup alarm for remaining runtime minus a second
    # signal.alarm((context.get_remaining_time_in_millis() / 1000) - 1)
    try:
        print('REQUEST RECEIVED:', event)
        print('REQUEST CONTEXT:', context)

        print("phone_number: ",item_value[key_name])
        phone_number = item_value[key_name]
        s = re.sub(r'[^a-zA-Z0-9]', '', phone_number)
        tabla_response = db_query(key_name,table,str(s))
        print(tabla_response)

    
        if tabla_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            responseBody =  {
                    "TEXT": {
                        "body": "The query response is {}".format(tabla_response['Items'][0])
                    }
            }
        else:
            responseBody =  {
                    "TEXT": {
                        "body": "The query with error {}".format(tabla_response['Items'][0])
                    }
                    }
            
        action_response = {
                'actionGroup': actionGroup,
                'function': function,
                'functionResponse': {
                    'responseBody': responseBody
                }

            }
            
        dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print("Response: {}".format(dummy_function_response))

        return dummy_function_response
            
    
    
    except Exception as error: 
        print('FAILED!', error)
        responseBody =  {
                    "TEXT": {
                        "body": "The query with error {}".format(error)
                    }
                    }
            
        action_response = {
                'actionGroup': actionGroup,
                'function': function,
                'functionResponse': {
                    'responseBody': responseBody
                }

            }
        dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print("Response: {}".format(dummy_function_response))

        return dummy_function_response
    
