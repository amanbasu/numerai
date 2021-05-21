import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

SENDER = 'AWS numerai <abc@xyz.com>'
RECIPIENT = 'abc@xyz.com'
AWS_REGION = 'ap-south-1'
SUBJECT = 'AWS - numerai submission'
ATTACHMENT = 'logs.txt'

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("AWS Numerai submission\r\nThis email was sent with Amazon SES using the AWS SDK for Python (boto3).")
            
# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>AWS Numerai submission</h1>
  <p>This email was sent with
    <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    <a href='https://aws.amazon.com/sdk-for-python/'>
      AWS SDK for Python (Boto)</a>.</p>
</body>
</html>
"""            

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a multipart/mixed parent container.
msg = MIMEMultipart('mixed')
# Add subject, from and to lines.
msg['Subject'] = SUBJECT 
msg['From'] = SENDER 
msg['To'] = RECIPIENT

# Create a multipart/alternative child container.
msg_body = MIMEMultipart('alternative')

# Encode the text and HTML content and set the character encoding. This step is
# necessary if you're sending a message with characters outside the ASCII range.
textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

# Add the text and HTML parts to the child container.
msg_body.attach(textpart)
msg_body.attach(htmlpart)

# Define the attachment part and encode it using MIMEApplication.
att = MIMEApplication(open(ATTACHMENT, 'rb').read())

# Add a header to tell the email client to treat this part as an attachment,
# and to give the attachment a name.
att.add_header('Content-Disposition', 'attachment', filename=ATTACHMENT)

# Attach the multipart/alternative child container to the multipart/mixed
# parent container.
msg.attach(msg_body)

# Add the attachment to the parent container.
msg.attach(att)

try:
    #Provide the contents of the email.
    client = boto3.client('ses', region_name=AWS_REGION)
    response = client.send_raw_email(
        Source=SENDER,
        Destinations=[RECIPIENT],
        RawMessage={'Data':msg.as_string()})
    print('Email sent: {}'.format(response))
except Exception as e:
    print('Exception occured: {}'.format(e))