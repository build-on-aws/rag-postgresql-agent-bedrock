import boto3
ssm = boto3.client('ssm')

def get_string_param(parameter_name):
    response = ssm.get_parameter(Name=parameter_name)
    parameter = response.get('Parameter')
    if parameter:
        return parameter.get('Value')
    else:
        return None