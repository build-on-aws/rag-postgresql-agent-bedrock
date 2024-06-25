from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class CreateAgentRole(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stk = Stack.of(self)
        _account = stk.account
        _region = stk.region
        _stack_name = stk.stack_name

        self.kb_service_role = iam.Role( self, "Kb",
                role_name= f'AmazonBedrockExecutionRoleForAgents_{_stack_name}',
                assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com",
                conditions={ 
                    "StringEquals": { "aws:SourceAccount": _account},
                    "ArnLike": { "aws:SourceArn": f"arn:aws:bedrock:{_region}:{_account}:agent/*"}
                }))
        
        self.kb_service_role.add_to_policy(iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[ "bedrock:InvokeModel"],
                resources=[ f"arn:aws:bedrock:{_region}::foundation-model/*"]))
        

        self.knowledge_base_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["bedrock:Retrieve"],
            resources=[f"arn:aws:bedrock:{_region}:{_account}:knowledge-base/*"])
        
        self.kb_service_role.add_to_policy(self.knowledge_base_policy)
        self.arn = self.kb_service_role.role_arn


        