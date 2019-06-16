import boto3


class Events:
    def __init__(self):
        self.evt = boto3.client('events')

    def put_rule(self, name, arn):
        # Put an event rule
        response = self.evt.put_rule(
            Name=name,
            RoleArn=arn,
            ScheduleExpression='rate(5 minutes)',
            State='ENABLED'
        )
        #print(response['RuleArn'])
