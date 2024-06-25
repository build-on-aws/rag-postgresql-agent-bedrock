from aws_cdk import (
    # Duration,
    Stack,SecretValue,
    # aws_sqs as sqs,
    RemovalPolicy,
    aws_dynamodb as ddb,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_s3_notifications,
    aws_s3 as s3,
    aws_lambda,
    aws_lambda_event_sources,
    aws_ssm as ssm,
)
from constructs import Construct
from lambdas import Lambdas
from apis import WebhookApi
from databases import Tables
from s3_cloudfront import S3Deploy

from get_param import get_string_param

agent_id = get_string_param("/agentvalue/agent_id")
alias_id = get_string_param("/agentvalue/alias_id")

class WhatsappAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        REMOVAL_POLICY = RemovalPolicy.DESTROY
        TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)
        AudioKeyName = "audio-from-whatsapp"
        TextBucketName = "text-to-whatsapp"
        
        DISPLAY_PHONE_NUMBER = 'YOU-NUMBER'

        stk = Stack.of(self)
        _account = stk.account
        _region = stk.region
        _stack_name = stk.stack_name

        #Whatsapp Secrets Values
        secrets = secretsmanager.Secret(self, "Secrets", secret_object_value = {
            'WHATS_VERIFICATION_TOKEN': SecretValue.unsafe_plain_text('WHATS_VERIFICATION_TOKEN'),
            'WHATS_PHONE_ID':SecretValue.unsafe_plain_text('WHATS_PHONE_ID'),
            'WHATS_TOKEN': SecretValue.unsafe_plain_text('WHATS_TOKEN')
           }) 
        
        Tbl = Tables(self, 'Tbl')

        Tbl.whatsapp_MetaData.add_global_secondary_index(index_name = 'jobnameindex', 
                                                            partition_key = ddb.Attribute(name="jobName",type=ddb.AttributeType.STRING), 
                                                            projection_type=ddb.ProjectionType.KEYS_ONLY)

        s3_deploy = S3Deploy(self, "-data", TextBucketName,TextBucketName)

        #Create Amazon Lambda Functions
        Fn  = Lambdas(self,'Fn')

        #Create Amazon API Gateweay
        Api = WebhookApi(self, "API", lambdas=Fn)

        # Amazon Lambda Function whatsapp_in - Config
        Fn.whatsapp_in.add_environment(key='CONFIG_PARAMETER', value=secrets.secret_arn)
        secrets.grant_read(Fn.whatsapp_in)

        Fn.whatsapp_in.add_environment(key='REFRESH_SECRETS', value='false')
        Fn.whatsapp_in.add_environment(key='DISPLAY_PHONE_NUMBER', value= DISPLAY_PHONE_NUMBER)

        Tbl.whatsapp_MetaData.grant_full_access(Fn.whatsapp_in)

        Fn.whatsapp_in.add_environment(key='whatsapp_MetaData', value=Tbl.whatsapp_MetaData.table_name)

        Fn.process_stream.add_environment( key='ENV_AGENT_BEDROCK', value=Fn.agent_bedrock.function_name)
        Fn.process_stream.add_environment(key='JOB_TRANSCRIPTOR_LAMBDA', value=Fn.audio_job_transcriptor.function_name)
        Fn.process_stream.add_environment(key='whatsapp_MetaData', value=Tbl.whatsapp_MetaData.table_name)
        Fn.process_stream.add_environment( key='WHATSAPP_OUT', value=Fn.whatsapp_out.function_name )
        
        Fn.process_stream.add_event_source(
            aws_lambda_event_sources.DynamoEventSource(table=Tbl.whatsapp_MetaData,
            starting_position=aws_lambda.StartingPosition.TRIM_HORIZON))
        Tbl.whatsapp_MetaData.grant_full_access(Fn.process_stream)
        

        # Amazon Lambda Function whatsapp_out - Config
        
        Fn.whatsapp_out.add_environment(key='ENV_INDEX_NAME', value="jobnameindex")
        Fn.whatsapp_out.add_environment(key='ENV_KEY_NAME', value="messages_id")

        Fn.whatsapp_out.grant_invoke(Fn.agent_bedrock)

        # Amazon Lambda Function audio_job_transcriptor - Config

        Fn.audio_job_transcriptor.add_to_role_policy(iam.PolicyStatement( actions=["transcribe:*"], resources=['*']))
        Fn.audio_job_transcriptor.add_environment(key='BucketName', value=s3_deploy.bucket.bucket_name)
        Fn.audio_job_transcriptor.add_environment(key='whatsapp_MetaData', value=Tbl.whatsapp_MetaData.table_name)
        Fn.audio_job_transcriptor.add_environment(key='AudioKeyName', value=AudioKeyName)
        Fn.audio_job_transcriptor.add_environment(key='TextBucketName', value=TextBucketName)
        Fn.audio_job_transcriptor.grant_invoke(Fn.process_stream)
        Fn.audio_job_transcriptor.add_to_role_policy(iam.PolicyStatement( actions=["dynamodb:*"], resources=[f"{Tbl.whatsapp_MetaData.table_arn}",f"{Tbl.whatsapp_MetaData.table_arn}/*"]))
        Fn.audio_job_transcriptor.add_environment(key='ENV_INDEX_NAME', value="jobnameindex")
        Fn.audio_job_transcriptor.add_environment(key='ENV_KEY_NAME', value="messages_id")  

        s3_deploy.bucket.grant_read_write(Fn.audio_job_transcriptor) 
        Tbl.whatsapp_MetaData.grant_full_access(Fn.audio_job_transcriptor) 

        # Amazon Lambda Function audio_job_transcriptor done - Config

        s3_deploy.bucket.grant_read(Fn.transcriber_done)

        s3_deploy.bucket.add_event_notification(s3.EventType.OBJECT_CREATED,
                                              aws_s3_notifications.LambdaDestination(Fn.transcriber_done),
                                              s3.NotificationKeyFilter(prefix=TextBucketName+"/"))
        
        Fn.transcriber_done.add_environment( key='WHATSAPP_OUT', value=Fn.whatsapp_out.function_name )
        Fn.transcriber_done.add_to_role_policy(iam.PolicyStatement( actions=["dynamodb:*"], resources=[f"{Tbl.whatsapp_MetaData.table_arn}",f"{Tbl.whatsapp_MetaData.table_arn}/*"]))
        Fn.transcriber_done.add_environment(key='ENV_INDEX_NAME', value="jobnameindex")
        Fn.transcriber_done.add_environment(key='ENV_KEY_NAME', value="messages_id")        

        Fn.whatsapp_out.grant_invoke(Fn.transcriber_done)

        Tbl.whatsapp_MetaData.grant_full_access(Fn.transcriber_done)

        Fn.transcriber_done.add_environment(key='whatsapp_MetaData', value=Tbl.whatsapp_MetaData.table_name)

        Fn.agent_bedrock.grant_invoke(Fn.transcriber_done)
        Fn.agent_bedrock.add_environment(key='ENV_AGENT_ID', value=agent_id)
        Fn.agent_bedrock.add_environment(key='ENV_ALIAS_ID', value=alias_id)
        Fn.agent_bedrock.add_environment( key='WHATSAPP_OUT', value=Fn.whatsapp_out.function_name )

        Fn.agent_bedrock.grant_invoke(Fn.process_stream)

        Fn.agent_bedrock.add_to_role_policy(
            iam.PolicyStatement( 
                actions=["bedrock:InvokeAgent"], 
                resources=[f"arn:aws:bedrock:{_region}:{_account}:*"]
                )
                )
    
        Fn.transcriber_done.add_environment( key='ENV_AGENT_BEDROCK', value=Fn.agent_bedrock.function_name)
        
        Fn.agent_bedrock.grant_invoke(Fn.transcriber_done)

        Tbl.whatsapp_MetaData.grant_full_access(Fn.agent_bedrock) 
