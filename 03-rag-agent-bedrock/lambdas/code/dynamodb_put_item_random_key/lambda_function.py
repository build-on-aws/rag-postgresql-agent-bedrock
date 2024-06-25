###########################################################
## This function is to put item with a random key value ###
###########################################################

import json
import csv
import boto3
import os
import time
import random

BASE_PATH = '/tmp/'
CSV_SEPARATOR = ';'

ddb = boto3.resource('dynamodb')
table = ddb.Table(os.environ['TABLE_NAME'])
key_name = os.environ.get('ENV_KEY_NAME')

def generate_random_4_digit_number():
    return random.randint(1000, 9999)

def save_item_ddb(table,item):
    response = table.put_item(Item=item)
    return response


def lambda_handler(event, contex):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])

    # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
    
    item_value = {}

    for n in parameters:
        print(n)
        item = n["name"]
        item_value[item] = n["value"]
        
    print(item_value)

    #Create a Random key value
    item_value[key_name] = str(generate_random_4_digit_number())
    print(f"{key_name}: ",item_value)
    response = save_item_ddb(table,item_value)
    print(response)
    
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        responseBody =  {
                "TEXT": {
                    "body": "The function {} was called successfully, value to database: ".format(item_value)
                }
            }
    else:
        responseBody =  {
                "TEXT": {
                    "body": "The function {} with error!".format(response)
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
    