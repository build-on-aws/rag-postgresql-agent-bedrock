from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as ddb,
    RemovalPolicy,
    aws_iam as iam,
    aws_bedrock as bedrock
    
    # aws_sqs as sqs,
)
from constructs import Construct

class CreateAgentWithKA(Construct):
    def __init__(self, scope: Construct, construct_id: str,agent_name,foundation_model, agent_instruction, description,agent_knowledge_base_property,agent_action_group_property,agent_resource_role, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)     

        self.cfn_agent = bedrock.CfnAgent(self, "LaInventadaAgent",
                    agent_name=agent_name,
                    description=description,
                    auto_prepare = True,
                    idle_session_ttl_in_seconds = 600,
                    skip_resource_in_use_check_on_delete=False,
                    test_alias_tags={
                        "test_alias_tags_key": "LaInventadaAgent"
                    },
                    knowledge_bases = agent_knowledge_base_property,
                    action_groups = agent_action_group_property,
                    agent_resource_role_arn = agent_resource_role,
                    foundation_model=foundation_model,
                    instruction=agent_instruction,
                    )
        self.cfn_agent.apply_removal_policy(RemovalPolicy.DESTROY)
        

        

