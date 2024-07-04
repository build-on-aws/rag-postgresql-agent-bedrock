# WhatsApp-Powered RAG Travel Support Agent: Elevating Customer Experience with PostgreSQL Knowledge Retrieval

In our previous blog post, "[Elevating Customer Support With a Whatsapp Assistant](https://community.aws/content/2bgPgouKvLhinu8bcE4LZQ1nnwv/elevating-customer-support-with-a-whatsapp-travel-assistant-from-las-vegas-mexico-to-las-vegas-nevada-a-re-invent-2023-history)," we explored how advanced technologies like Generative AI and Retrieval Augmented Generation (RAG) can revolutionize traditional customer support models in the travel industry. Today, we'd like to present an alternative approach that leverages the power of [Agents for Amazon Bedrock](https://aws.amazon.com/bedrock/agents/), a vectorized [Amazon Aurora](https://docs.aws.amazon.com/es_es/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html) a PostgreSQL [knowledge base for Amazon Bedrock](https://aws.amazon.com/bedrock/knowledge-bases/).

This architecture eliminates the need for complex conversation management logic, as Bedrock agents handle session tracking, while the Knowledge Base for Amazon Bedrock using Aurora PostgreSQL ensures highly accurate and contextual responses, and [Amazon DynamoDB](https://aws.amazon.com/pm/dynamodb) serves a dual purpose: storing both passenger information and support tickets.

Key features of our solution include:
1. Intelligent query handling using RAG technique.
2. Personalized support based on individual traveler data.
3. Automatic creation of support tickets for unresolved issues.
4. Ability to query and manage the support ticket database.

This application is built in four stages using infrastructure as code with [AWS Cloud Development Kit (CDK)](https://aws.amazon.com/cdk) for python. In the first stage, an Amazon Aurora PostgreSQL vector database is set up. In the second stage, the Knowledge Base for Amazon Bedrock is created using the established database. The third stage involves creating an Amazon Bedrock agent. And in the fourth stage, a WhatsApp application is deployed to provide the user interface for the system.

![Digrama parte 1](/imagen/diagram_1.jpg)


✅ **AWS Level**: Advanced - 300   

**Prerequisites:**
-  [Foundational knowledge of Python](https://catalog.us-east-1.prod.workshops.aws/workshops/3d705026-9edc-40e8-b353-bdabb116c89c/)
- [AWS Account](https://aws.amazon.com/resources/create-account/?sc_channel=el&sc_campaign=datamlwave&sc_content=cicdcfnaws&sc_geo=mult&sc_country=mult&sc_outcome=acq) 
- [Enable model Access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for the following models:
    - Amazon Titan Embeddings V2
    - Anthropic Claude 3 models (Haiku or Sonnet).
- [Set up the AWS Command Line Interface (CLI)](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
- [Read about AWS CDK "Get started with Python"](https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html)
- [Optional: Bootstrap your account/region if this is your first CDK Project](https://docs.aws.amazon.com/cdk/v2/guide/hello_world.html#hello_world_bootstrap)


💰 **Cost To Complete**: 
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)  Note: in this project, we use Amazon Titan Embeddings v2 and Anthropic Claude 3
- [Amazon S3 Pricing](https://aws.amazon.com/s3/pricing/)
- [AWS Systems Manager pricing](https://aws.amazon.com/systems-manager/pricing/)
- [Amazon Aurora Pricing](https://aws.amazon.com/rds/aurora/pricing/) Note: Here we use Aurora Serverless with 0.5 ACU
- [Amazon Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
- [Amazon DynamoDB Pricing](https://aws.amazon.com/dynamodb/pricing/)
- [Whatsapp pricing](https://developers.facebook.com/docs/whatsapp/pricing/)
- [Amazon ApiGateway](https://aws.amazon.com/api-gateway/pricing/)
- [Amazon Transcribe Pricing](https://aws.amazon.com/transcribe/pricing/)


> 🚨 **Note**: This series of CDK stacks should be deployed within the same AWS account and region. This is because each stack is created to store essential information in a [AWS Systems Manager (SSM) Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) secret, which is subsequently retrieved by the stack in the next step of the deployment process.

## This is what you are going to build:

![Digrama parte 1](/imagen/diagram_2.png)

1. **Inbound Message Webhook:**
    
    The process begins when a user sends a voice note/text message via WhatsApp. The voice/text message is received through an Amazon API Gateway and processed by AWS Lambda Function.
    
    The message details are stored in Amazon DynamoDB table for decoupling and processing.

1. **Audio Text Process:**
    
    If there is a  voice message, it is stored in an Amazon S3 bucket. Then, Amazon Transcribe converts the audio to text, which is sent to the assistant.

    If it is only a text message it will go directly to the assitant input.

3. **Assistant Response:** 


    The Agent processes the query and generates a response, potentially accessing additional data from DynamoDB table or a knowledge base.
    
    Depending on the user's request, various actions can be triggered, such as creating support tickets or retrieving passenger information.
    
    The final response is sent back to the user via WhatsApp.

## Let's build!

## Part 0: Clone the repo

```zsh
git clone https://github.com/build-on-aws/rag-postgresql-agent-bedrock
```
## Part 1: [Building an Amazon Aurora PostgreSQL vector database as a Knowledge Base for Amazon Bedrock.](https://github.com/build-on-aws/rag-postgresql-agent-bedrock/tree/main/01-create-aurora-pgvector#readme)

For setting up an Amazon Aurora PostgreSQL vector database. It explains the importance of vector databases for implementing Retrieval Augmented Generation (RAG).  AWS Cloud Development Kit (CDK) for Python is used to set up the database infrastructure. This  also includes detailed steps for preparing the database, such as installing extensions, creating schemas and roles, and setting up tables and indexes using Custom Constructs. 

## Part 2: [Building a Knowledge Base for Amazon Bedrock using Aurora PostgreSQL.](https://github.com/build-on-aws/rag-postgresql-agent-bedrock/tree/main/02-create-bedrock-knowledge-bases#readme)

 It focuses on creating a Knowledge Base for Amazon Bedrock, which involves setting up an S3 bucket as a data source, configuring necessary IAM roles and permissions, and storing information in AWS Systems Manager Parameter Store. The Knowledge Base automatically processes unstructured text data from PDFs, converts it into text chunks, generates vector embeddings, and stores them in a PostgreSQL database. The guide provides step-by-step instructions for setup and  deployment.

## Part 3: [Building an Agent for Amazon Bedrock to Search Knowledge Base and Manage Amazon DynamoDB Data.](https://github.com/build-on-aws/rag-postgresql-agent-bedrock/tree/main/03-rag-agent-bedrock#readme)

The project demonstrates how to build an AI-powered agent capable of querying and analyzing data stored in a PostgreSQL database using natural language prompts.

## Part 4: [Enhanced User Interaction: Integrating a WhatsApp Assistant with Amazon Bedrock Agent.](https://github.com/build-on-aws/rag-postgresql-agent-bedrock/tree/main/04-whatsapp-app#readme)

The final part of a four-part series on building an advanced WhatsApp-powered RAG Travel Support Agent using Amazon Bedrock Agent. The project integrates various AWS services, including API Gateway, Lambda, DynamoDB, S3, and Transcribe, to create a workflow for processing and responding to user messages. The application can handle both text and voice messages, transcribe audio, and leverage a knowledge base built on Aurora PostgreSQL for information retrieval. 

>👾 **Tip:** If you don't want to use WhatsApp, that's fine! You can use the following JavaScript application, which creates a UI that allows you to use the Agents and Knowledge Bases for Amazon Bedrock available in your AWS account --> [Building ReactJS Generative AI apps with Amazon Bedrock and AWS JavaScript SDK](https://github.com/build-on-aws/building-reactjs-gen-ai-apps-with-amazon-bedrock-javascript-sdk)


## Conclusion

This enhanced WhatsApp Travel Assistant demonstrates the power of AWS's integrated AI and database services. By leveraging Amazon Bedrock's agent and knowledge base capabilities, along with Aurora PostgreSQL and DynamoDB, we've created a more streamlined, powerful, and maintainable solution.

The addition of the support ticket system provides a complete end-to-end customer service experience, allowing for seamless escalation of complex issues while maintaining the benefits of AI-powered initial interactions.

We encourage you to build upon this foundation, perhaps by expanding the knowledge base, changing the agent's responses, or integrating with additional services.

Thank you for joining us on this journey to revolutionize travel customer support with AWS technologies!


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

