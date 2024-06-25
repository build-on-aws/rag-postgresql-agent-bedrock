###############################################################
## This function is to populate a dynamoDB table with a CSV ###
###############################################################

import json
import requests
import boto3
import botocore.exceptions
import csv  
import json  


dynamodb = boto3.resource('dynamodb')



def lambda_handler(event, context):
    '''Handle Lambda event from AWS'''
    # Setup alarm for remaining runtime minus a second
    # signal.alarm((context.get_remaining_time_in_millis() / 1000) - 1)
    try:
       
        print('REQUEST RECEIVED:', event)
        print('CONTEXT RECEIVED:', context)

        if event['RequestType'] == 'Create':
            print('CREATE!')
            event['PhysicalResourceId'] = 'NOT_YET'
            load_data(event, context)

        elif event['RequestType'] == 'Update':
            print('UPDATE!')
            load_data(event, context)
            send_response(event, context, "SUCCESS",{"Message": "Resource update successful!"})

        elif event['RequestType'] == 'Delete':
            print('DELETE!')
            send_response(event, context, "SUCCESS",{"Message": "Resource delete successful!"})
        else:
            print('FAILED!')
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event received from CloudFormation"})
    except Exception as error: 
        print('FAILED!', error)
        send_response(event, context, "FAILED", {
            "Message": "Exception during processing"})


def load_data (event, context):
    
    if "ResourceProperties" in event:
        print ("create_datasource")
        props = event['ResourceProperties']
        
        print("props:",props)
        table_name = props['table_name']
        sample_data_file = props['sample_data_file']
        table = dynamodb.Table(table_name)

        rows = []


        with open(sample_data_file) as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                rows.append(dict(row)) 


        with table.batch_writer() as batch:
            for item in rows:
                batch.put_item(Item=item)


        event['PhysicalResourceId'] = f"{table_name}|{len(rows)}"
        send_response(event, context, "SUCCESS",{"Message": "Resource creation successful!"})

    else:
        print("no resource properties!")


def send_response(event, context, response_status, response_data):
    '''Send a resource manipulation status response to CloudFormation'''
    response_body = json.dumps({
        "Status": response_status,
        "Reason": "See the details in CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": event['PhysicalResourceId'] if 'PhysicalResourceId' in event else "NOPHYID",
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    })
    headers = {
    'Content-Type': 'application/json',  
    'Content-Length': str(len(response_body))
    } 


    print('ResponseURL: ', event['ResponseURL'])
    print('ResponseBody:', response_body)

    response = requests.put(event['ResponseURL'], 
                            data=response_body, headers=headers)
    
    print("Status code:", response.status_code)
    print("Status message:", response.text)

    return response


def timeout_handler(_signal, _frame):
    '''Handle SIGALRM'''
    raise Exception('Time exceeded')

# signal.signal(signal.SIGALRM, timeout_handler)
