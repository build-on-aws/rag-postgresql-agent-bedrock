import sys

from aws_cdk import aws_lambda, Duration, aws_iam as iam

from constructs import Construct


LAMBDA_TIMEOUT = 900

BASE_LAMBDA_CONFIG = dict(
    timeout=Duration.seconds(LAMBDA_TIMEOUT),
    memory_size=128,
    tracing=aws_lambda.Tracing.ACTIVE,
    architecture=aws_lambda.Architecture.ARM_64
)

PYTHON_LAMBDA_CONFIG = dict(
    runtime=aws_lambda.Runtime.PYTHON_3_11, **BASE_LAMBDA_CONFIG
)

from layers import Layers

class Lambdas(Construct):
    def __init__(self, scope: Construct, construct_id: str, self_account, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        COMMON_LAMBDA_CONF = dict(environment={}, **PYTHON_LAMBDA_CONFIG)

        Lay = Layers(self, 'Lay')

        self.dynamodb_put_item = aws_lambda.Function(
            self, "DynamoDB_put_item", 
            description ="Put items to csv to DynamoDB" ,
            handler="lambda_function.lambda_handler",
            layers= [Lay.bs4_requests, Lay.common],
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_put_item_from_csv"),
            **COMMON_LAMBDA_CONF)

        
        self.dynamodb_query_passanger = aws_lambda.Function(
            self, "query_dynamodb_passanger", 
            description ="Query DynamoDB Passanger Table" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_query"),
            **COMMON_LAMBDA_CONF)
        
        self.dynamodb_query_ticket = aws_lambda.Function(
            self, "query_dynamodb_ticket", 
            description ="Query DynamoDB Ticket Table" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_query"),
            **COMMON_LAMBDA_CONF)
        
        self.ask_date = aws_lambda.Function(
            self, "ask_date", 
            description ="Ask today Date" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/ask_date"),
            **COMMON_LAMBDA_CONF)

        self.dynamodb_put_item_random_key = aws_lambda.Function(
            self, "dynamodb_put_item_random_key", 
            description ="put item with a random key value" ,
            handler="lambda_function.lambda_handler",
            code=aws_lambda.Code.from_asset("./lambdas/code/dynamodb_put_item_random_key"),
            **COMMON_LAMBDA_CONF)
        
        for f in [self.dynamodb_query_passanger,self.ask_date,self.dynamodb_query_ticket,self.dynamodb_put_item_random_key]:
            f.add_permission(
                    f'invoke from account',
                    principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
                    action="lambda:invokeFunction",
                    # source_arn=f"arn:aws:lambda:{self.region}:{self.account}:*")
                    )
