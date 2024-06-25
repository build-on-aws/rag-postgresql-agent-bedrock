###############################################################
## This function is to populate a dynamoDB table with a CSV ###
###############################################################

import datetime


BASE_PATH = '/tmp/'
CSV_SEPARATOR = ';'


def lambda_handler(event, contex):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']

    # Obtener la fecha y hora actual
    ahora = datetime.datetime.now()

    # Obtener el día de la semana
    dia_semana = ahora.strftime("%A")

    # Obtener la fecha en formato día/mes/año
    fecha = ahora.strftime("%d/%m/%Y")

    # Obtener la hora en formato hora:minutos:segundos
    hora = ahora.strftime("%H:%M:%S")

    # Imprimir el resultado
    print(f"Today is {dia_semana}, {fecha}")
    print(f"Date {hora}")

    today = {"day": dia_semana, "date": fecha, "time": hora}
  
    responseBody =  {
                "TEXT": {
                    "body": "The date and hour from today is {}".format(today)
                }
            }
    print("Response: {}".format(responseBody))

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
    