from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_bedrock as bedrock,
    custom_resources as cr,
    aws_ssm as ssm,
)
from constructs import Construct
from knowledge_base import KnowledgeBases, KnowledgeBaseDatasource
from s3_cloudfront import S3Deploy
from kb_role import CreateKBRole

from get_param import get_string_param
from s3_cloudfront import S3Deploy


model_id = "amazon.titan-embed-text-v2:0"
credentialsSecretArn = get_string_param("/pgvector/secret_arn")
resourceArn_aurora = get_string_param("/pgvector/cluster_arn")
ssm_table_name = get_string_param("/pgvector/table_name")
tableName = f"bedrock_integration.{ssm_table_name}"

common_kb_property = dict(
    credentialsSecretArn = credentialsSecretArn,
    databaseName = "kbdata",
    metadataField = "metadata",
    primaryKeyField = "id",
    textField = "chunks",
    vectorField = "embedding",
    resourceArn = resourceArn_aurora,
    tableName = tableName
)

class CreateBedrockKnowledgeBasesStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        _region = stk.region

        s3_deploy = S3Deploy(self, "S3Deploy", "airline-qa-base", "airline-qa-base")

        bucket_name = s3_deploy.bucket.bucket_name
        bucketArn = s3_deploy.bucket.bucket_arn

        kb_service_role = CreateKBRole( self, "CreateKBRole", credentialsSecretArn, bucket_name)

        base_kb_property = dict(
            embeddingModelArn = f"arn:aws:bedrock:{_region}::foundation-model/{model_id}",
            roleArn =  kb_service_role.arn, **common_kb_property)
        description = "documents regarding to help the passenger"
        # Bedrock Knowledge Base
        bedrock_kb_property = dict(description = description, name= "la-inventada-airlines-knowledge-base", **base_kb_property)
        bedrock_kb = KnowledgeBases(self, "KB1", bedrock_kb_property)
        bedrock_kb.node.add_dependency(kb_service_role)
        bedrock_ds  = KnowledgeBaseDatasource(self, "DS1", bedrock_kb.kb_id, "Bedrock-airlines-qa", bucketArn, "airline-qa-base",description)

        bedrock_ds.node.add_dependency(s3_deploy.s3deploy)

        ssm.StringParameter( self, "kb_ssm", parameter_name=f"/pgvector/kb_id", string_value=bedrock_kb.kb_id) 
