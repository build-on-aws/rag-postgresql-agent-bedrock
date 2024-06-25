        
from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    CustomResource,
    CfnOutput
)
from constructs import Construct
from databases import Tables
from lambdas import Lambdas


class DynamodbWithSampleDataStack(Construct):
    def __init__(
            self, scope: Construct, 
            construct_id: str,
            table,
            lambda_function,
            file_name,
            **kwargs) -> None:
        
        super().__init__(scope, construct_id, **kwargs)


        table.grant_full_access(lambda_function)
        CfnOutput(self, "table", value=table.table_name)
        
        ds = CustomResource(
            self,
            "S3DS",
            resource_type="Custom::CSVDataSource",
            service_token=lambda_function.function_arn,
            properties=dict(
                table_name=table.table_name, sample_data_file=file_name
            ),
        )
        