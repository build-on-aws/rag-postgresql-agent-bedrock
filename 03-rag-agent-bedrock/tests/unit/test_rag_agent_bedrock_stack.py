import aws_cdk as core
import aws_cdk.assertions as assertions

from rag_agent_bedrock.rag_agent_bedrock_stack import RagAgentBedrockStack

# example tests. To run these tests, uncomment this file along with the example
# resource in rag_agent_bedrock/rag_agent_bedrock_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = RagAgentBedrockStack(app, "rag-agent-bedrock")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
