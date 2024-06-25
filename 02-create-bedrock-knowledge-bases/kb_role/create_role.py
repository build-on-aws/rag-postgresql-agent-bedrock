from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class CreateKBRole(Construct):

    def __init__(self, scope: Construct, construct_id: str,credentialsSecretArn,bucket_name, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        stk = Stack.of(self)


        self.kb_service_role = iam.Role(
                self,
                "KbServiceRole",
                assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": stk.account
                    },
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:bedrock:{stk.region}:{stk.account}:knowledge-base/*"
                    }
                })
            )
        
        self.kb_service_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
            ],
            resources= [
                f"arn:aws:bedrock:{stk.region}::foundation-model/*"
            ]
            
        ),
        )
        self.kb_service_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "secretsmanager:GetSecretValue",
            ],
            resources= [
                credentialsSecretArn
            ]
            
        ),
        )
        self.kb_service_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "rds:DescribeDBClusters",
                "rds-data:BatchExecuteStatement",
                "rds-data:ExecuteStatement"
            ],
            resources= [f"arn:aws:rds:{stk.region}:{stk.account}:cluster:*"]
            
        ),
        )
        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_iam/ManagedPolicyProps.html
        
        ListBucket_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:ListBucket",
            ],
            resources=[
                f"arn:aws:s3:::{bucket_name}",
            ],
            conditions={
                "StringEquals": {
                    "aws:ResourceAccount": [stk.account]
                }
            })
        
        self.kb_service_role.add_to_policy(ListBucket_policy)

        GetObjectStatement_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:Get*",
            ],
            resources=[
                f"arn:aws:s3:::{bucket_name}/*",
            ],
            conditions={
                "StringEquals": {
                    "aws:ResourceAccount": [ stk.account]
                }
            })
        
        self.kb_service_role.add_to_policy(GetObjectStatement_policy)

        

        self.kb_service_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonRDSFullAccess"))

        self.arn = self.kb_service_role.role_arn
        