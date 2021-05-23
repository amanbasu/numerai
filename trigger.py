import json
import boto3

region = '<your-region>'
instance = '<your-instance-id>'
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    
    ec2.start_instances(InstanceIds=[instance])

    return {
        'statusCode': 200,
        'body': json.dumps('Instance started successful.')
    }
