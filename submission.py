import json
import boto3

region = '<your-region>'
instance = '<your-instance-id>'
ssm = boto3.client('ssm')

def lambda_handler(event, context):
    
    command = 'sudo -i -u ec2-user /home/ec2-user/run.sh'
    ssmresponse = ssm.send_command(InstanceIds=[instance], 
                                    DocumentName='AWS-RunShellScript', 
                                    Parameters={'commands':[command]})

    return {
        'statusCode': 200,
        'body': json.dumps('Command successful.')
    }
