def create_kb_property(kb_data):
        kb_group_properties = []
        for n in kb_data: 
             kb_group_property = bedrock.CfnAgent.AgentKnowledgeBaseProperty(
                    description=n["description_kb"],
                    knowledge_base_id=n["knowledge_base_id"],
        )
        kb_group_properties.append(kb_group_property)
        return kb_group_properties
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
