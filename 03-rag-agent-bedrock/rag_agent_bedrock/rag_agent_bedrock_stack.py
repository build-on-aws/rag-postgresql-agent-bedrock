from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as ddb,
    SecretValue,
    RemovalPolicy,
    aws_iam as iam,
    aws_bedrock as bedrock,
    aws_secretsmanager as secretsmanager,
    aws_ssm as ssm,

)
from constructs import Construct

from agent_bedrock import CreateAgentWithKA
from databases import Tables
from lambdas import (Lambdas,DynamodbWithSampleDataStack)
from agent_role import CreateAgentRole
import os
import json

from get_param import get_string_param

# ############
# The provided code block is a Python function called 
#create_kb_property
# that takes a kb_data.json
# parameter, which is likely a list of dictionaries 
# representing knowledge base data.
# ###########
def create_kb_property(kb_data):
        kb_group_properties = []
        for n in kb_data: 
             kb_group_property = bedrock.CfnAgent.AgentKnowledgeBaseProperty(
                    description=n["description_kb"],
                    knowledge_base_id=n["knowledge_base_id"],
        )
        kb_group_properties.append(kb_group_property)
        return kb_group_properties

# #######
# The provided code block is a Python function called 
# agent_action_group_property that takes an ag_data.json
# parameter, which is likely a list of dictionaries
# representing agent action group data.
# #######

def agent_action_group_property(ag_data):
    agent_action_group_properties = []
    agent_action_group_property = bedrock.CfnAgent.AgentActionGroupProperty(
                        action_group_name="askinuput",
                        parent_action_group_signature="AMAZON.UserInput",
                        #skip_resource_in_use_check_on_delete=False
                            )
    agent_action_group_properties.append(agent_action_group_property)
    for n in ag_data: 
        parameters = {}
        for p in n["functions"]["parameters"]:
            parameters[p["name"]] = bedrock.CfnAgent.ParameterDetailProperty(
                                            type=p["type"],

                                            # the properties below are optional
                                            description=p["description"],
                                            required=bool(p["required"])
                                        )

        agent_action_group_property = bedrock.CfnAgent.AgentActionGroupProperty(
                                action_group_name=n["action_group_name"],

                                # the properties below are optional
                                action_group_executor=bedrock.CfnAgent.ActionGroupExecutorProperty(
                                    lambda_=n["lambda_"]
                                    ),
                                
                                action_group_state="ENABLED",
                                #description=n["description"],
                                function_schema=bedrock.CfnAgent.FunctionSchemaProperty(
                                    functions=[bedrock.CfnAgent.FunctionProperty(
                                        name=n["functions"]["name"],
                                        # the properties below are optional
                                        description=n["functions"]["description"],
                                        parameters=parameters
                                    )]
                                ),
                                #parent_action_group_signature="AMAZON.UserInput",
                                skip_resource_in_use_check_on_delete=False
                            )
        agent_action_group_properties.append(agent_action_group_property)
    return agent_action_group_properties

REMOVAL_POLICY = RemovalPolicy.DESTROY
TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)
AudioKeyName = "audio-from-whatsapp"
TextBucketName = "text-to-whatsapp"
DISPLAY_PHONE_NUMBER = 'YOU-NUMBER'

ssm_kb_id = get_string_param("/pgvector/kb_id")

class RagAgentBedrockStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        stk = Stack.of(self)
        ACCOUNT_ID = stk.account
        REGION = self.region

        ENV_KEY_NAME = "date"
        env_key_sec_global = "phone_number"
        file_path_ag_data = './rag_agent_bedrock/ag_data.json'
        file_path_agent_data = './rag_agent_bedrock/agent_data.json'
        file_path_kb_data = './rag_agent_bedrock/kb_data.json'
        agent_prompt = './rag_agent_bedrock/agent_prompt.txt'

        Fn  = Lambdas(self,'Fn',ACCOUNT_ID)
        Tbl = Tables(self, 'Tbl')

        with open(file_path_agent_data, 'r') as file:
            agent_data = json.load(file)

        with open(agent_prompt, 'r', encoding='utf-8') as f:
            improved_prompt = f.read()

        agent_data["agent_instruction"] = improved_prompt

         #ag_data exists
        if  os.path.exists(file_path_ag_data): 
             with open(file_path_ag_data, 'r') as file:
                  ag_data = json.load(file)
            #add lambda arn to action group data
             ag_data[0]["lambda_"] = Fn.dynamodb_query_passanger.function_arn
             ag_data[1]["lambda_"] = Fn.ask_date.function_arn
             ag_data[2]["lambda_"] = Fn.dynamodb_put_item_random_key.function_arn
             ag_data[3]["lambda_"] = Fn.dynamodb_query_ticket.function_arn

        #kb_data exists
        if  os.path.exists(file_path_kb_data): 
             with open(file_path_kb_data, 'r') as file:
                  kb_data = json.load(file)
                  kb_data[0]["knowledge_base_id"] = ssm_kb_id
        else:
             kb_data = None

        Tbl.passangerTable.grant_full_access(Fn.dynamodb_put_item)
        
        # Load data into table
        DynamodbWithSampleDataStack(
            self, "pasanger-qa-base",
            lambda_function=Fn.dynamodb_put_item,
            table= Tbl.passangerTable,
            file_name = "dataset.csv" 
        )

        Fn.dynamodb_query_passanger.add_environment(key='TABLE_NAME', value=Tbl.passangerTable.table_name)
        Fn.dynamodb_query_passanger.add_environment(key='ENV_KEY_NAME', value="passenger_id")
        Tbl.passangerTable.grant_full_access(Fn.dynamodb_query_passanger)

        Fn.dynamodb_query_ticket.add_environment(key='TABLE_NAME', value=Tbl.ticketTable.table_name)
        Fn.dynamodb_query_ticket.add_environment(key='ENV_KEY_NAME', value="ticket_number")
        Tbl.ticketTable.grant_full_access(Fn.dynamodb_query_ticket)

        Fn.dynamodb_put_item_random_key.add_environment(key='TABLE_NAME', value=Tbl.ticketTable.table_name)
        Fn.dynamodb_put_item_random_key.add_environment(key='ENV_KEY_NAME', value="ticket_number")
        Tbl.ticketTable.grant_full_access(Fn.dynamodb_put_item_random_key)
        
        agent_name = "assistant-for-la-inventada-airlines-q-about-users-creates-queries-support-tickets"
        print("Create La Inventada Agent")
        agent_action_group_properties = agent_action_group_property(ag_data)
        agent_knowledge_base_property =create_kb_property(kb_data) 

        # Agent Execution Role    
        agent_resource_role = CreateAgentRole(self, "role")

        agent = CreateAgentWithKA(self, "agentwithbooth", agent_name, agent_data["foundation_model"], agent_data["agent_instruction"], agent_data["description"], agent_knowledge_base_property, agent_action_group_properties, agent_resource_role.arn)    

        agent_id = agent.cfn_agent.attr_agent_id

        #https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_bedrock/CfnAgentAlias.html

        agent_alias = bedrock.CfnAgentAlias(self, "MyCfnAgentAlias",
                agent_alias_name="AgenteLaInventada",
                agent_id=agent_id,
                # the properties below are optional
                description="Agente La Inventada",
                
            )    
        
        ssm.StringParameter( self, "agentid_ssm", parameter_name=f"/agentvalue/agent_id", string_value=agent_id)
        ssm.StringParameter( self, "aliasid_ssm", parameter_name=f"/agentvalue/alias_id", string_value=agent_alias.attr_agent_alias_id) 
