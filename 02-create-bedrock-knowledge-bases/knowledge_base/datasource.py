from aws_cdk import aws_bedrock as bedrock, custom_resources as cr

from constructs import Construct



# https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrock/CfnDataSource.html

class KnowledgeBaseDatasource(Construct):
    def __init__(self, scope: Construct, construct_id: str, kb_id, ds_name, bucketArn, bucket_key,description, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.datasource = bedrock.CfnDataSource(
            self,
            "KBSampleDataSource",
            data_source_configuration=bedrock.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=bedrock.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_arn=bucketArn, inclusion_prefixes=[f"{bucket_key}/"]
                ),
                type="S3",
            ),
            knowledge_base_id=kb_id,
            name=ds_name,
            data_deletion_policy="DELETE",
            description=description,
            vector_ingestion_configuration=bedrock.CfnDataSource.VectorIngestionConfigurationProperty(
                chunking_configuration=bedrock.CfnDataSource.ChunkingConfigurationProperty(
                    chunking_strategy="FIXED_SIZE",
                    fixed_size_chunking_configuration=bedrock.CfnDataSource.FixedSizeChunkingConfigurationProperty(
                        max_tokens=300, overlap_percentage=20
                    ),
                )
            ),
        )

        my_cr = cr.AwsCustomResource(
            self,
            "SyncDatasource",
            on_update=cr.AwsSdkCall(  # will also be called for a CREATE event
                service="@aws-sdk/client-bedrock-agent",
                action="StartIngestionJob",
                parameters={"dataSourceId": self.datasource.attr_data_source_id, "knowledgeBaseId": kb_id},
                physical_resource_id=cr.PhysicalResourceId.from_response("ingestionJob.ingestionJobId"),
            ),
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
        )

        my_cr.node.add_dependency(self.datasource)  