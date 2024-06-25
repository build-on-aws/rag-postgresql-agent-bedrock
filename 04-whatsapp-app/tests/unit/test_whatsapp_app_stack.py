import aws_cdk as core
import aws_cdk.assertions as assertions

from whatsapp_app.whatsapp_app_stack import WhatsappAppStack

# example tests. To run these tests, uncomment this file along with the example
# resource in whatsapp_app/whatsapp_app_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WhatsappAppStack(app, "whatsapp-app")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
