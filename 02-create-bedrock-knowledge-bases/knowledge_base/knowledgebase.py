from aws_cdk import (
    aws_bedrock as bedrock,
    RemovalPolicy
    )
from constructs import Construct


class KnowledgeBases(Construct):
    def __init__(self, scope: Construct, construct_id: str, kb_property, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a knowledge base
        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrock/CfnKnowledgeBase.html#storageconfigurationproperty
        self.KnowledgeBases = bedrock.CfnKnowledgeBase(self, "MyCfnKnowledgeBase",
                        knowledge_base_configuration=bedrock.CfnKnowledgeBase.KnowledgeBaseConfigurationProperty(
                            type="VECTOR",
                            vector_knowledge_base_configuration=bedrock.CfnKnowledgeBase.VectorKnowledgeBaseConfigurationProperty(
                                embedding_model_arn=kb_property["embeddingModelArn"]
                            )
                        ),
                        name=kb_property["name"],
                        role_arn=kb_property["roleArn"],
                        storage_configuration=bedrock.CfnKnowledgeBase.StorageConfigurationProperty(
                            #type for rds aurora
                            type="RDS",
                            rds_configuration=bedrock.CfnKnowledgeBase.RdsConfigurationProperty(
                            credentials_secret_arn=kb_property["credentialsSecretArn"],
                            database_name=kb_property["databaseName"],
                            field_mapping=bedrock.CfnKnowledgeBase.RdsFieldMappingProperty(
                                metadata_field=kb_property["metadataField"],
                                primary_key_field=kb_property["primaryKeyField"],
                                text_field=kb_property["textField"],
                                vector_field=kb_property["vectorField"]
                            ),
                            resource_arn=kb_property["resourceArn"],
                            table_name=kb_property["tableName"]
                        )
                    ),

                    # the properties below are optional
                    description=kb_property["description"],
                                        )
        self.KnowledgeBases.apply_removal_policy(RemovalPolicy.DESTROY)

        self.kb_id = self.KnowledgeBases.attr_knowledge_base_id
        