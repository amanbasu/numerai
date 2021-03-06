# Numerai on AWS

This repo contains the code to build your own [numerai](https://numer.ai/tournament) compute instance on AWS.

## Steps
1. Setup your EC2 instance environment to run the numerai submission scripts.
- refer to [env_setup.sh](env_setup.sh) file to setup the numerai environment.
- modify [predict.py](predict.py) according to your model needs.
- use [run.sh](run.sh) to execute the prediction scripts.

*Note: I have used `t2.large` instance type.*

2. Define Lambda function to trigger your instance. I have used 2 functions - one to start the instance and another to trigger the submission script.
- [trigger.py](trigger.py) starts the EC2 instance.
- [submission.py](submission.py) uses SSM to execute command on the instance after it has been started.

3. Define EventBridge rules to trigger your Lambda functions.
- first rule triggers the Lambda to start the instance. Event schedule is `cron(0 0 ? * SUN *)`.
- second rule triggers the Lambda to execute commands. Event schedule is `cron(1 0 ? * SUN *)` (a minute after the first one).

## Permissions
1. EC2
- **AmazonEC2RoleforSSM:** to let Lambda function exuecute commands using SSM.
- **SendRawEmail:** to let EC2 send emails via SES.

2. Lambda
- **StartInstances:** to start EC2 instance from Lambda.
- **AmazonSSMFullAccess:** to execute commands inside EC2.

*Note: Instead of giving full access, more fine-grained permissions are recommended.*
