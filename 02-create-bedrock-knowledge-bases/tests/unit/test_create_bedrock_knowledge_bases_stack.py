import aws_cdk as core
import aws_cdk.assertions as assertions

from create_bedrock_knowledge_bases.create_bedrock_knowledge_bases_stack import CreateBedrockKnowledgeBasesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in create_bedrock_knowledge_bases/create_bedrock_knowledge_bases_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CreateBedrockKnowledgeBasesStack(app, "create-bedrock-knowledge-bases")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
