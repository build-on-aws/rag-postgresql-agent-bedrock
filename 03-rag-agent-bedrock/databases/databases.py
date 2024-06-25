from aws_cdk import (
    RemovalPolicy,
    aws_dynamodb as ddb
)
from constructs import Construct


REMOVAL_POLICY = RemovalPolicy.DESTROY

TABLE_CONFIG = dict (removal_policy=REMOVAL_POLICY, billing_mode= ddb.BillingMode.PAY_PER_REQUEST)


class Tables(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
                   
        self.passangerTable = ddb.Table(
            self, "passangerTable", 
            partition_key=ddb.Attribute(name="passenger_id", type=ddb.AttributeType.STRING),
            **TABLE_CONFIG)
        
        self.ticketTable = ddb.Table(
            self, "ticketTable", 
            partition_key=ddb.Attribute(name="ticket_number", type=ddb.AttributeType.STRING),
            **TABLE_CONFIG)
                                    
        