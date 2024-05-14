import re

import boto3
from botocore.exceptions import ClientError


def clean_html(raw_html):
    cleaner = re.compile('<.*?>')
    clean_text = re.sub(cleaner, '', raw_html)
    return clean_text


EMAIL_TEMPLATES = {
    "experiment_created": {
        "subject": "S2F - New Experiment Created",
        "body": """<html>
            <head></head>
            <body>
                <h1>Experiment Successfully Registered</h1>

                <p>Thanks for using the S2F prediction service,</p>

                <p>Your job {alias}, was registered on our service on {date}.
                Below, you can find a link to track the progress of the
                experiment, as well as the downloadable results.</p>

                <p>Results are not kept in our servers indefinitely, and will
                be deleted when space is required for other experiments in the
                queue. We can only ensure the files remain in the server for
                24 hours.</p>

                <p>This is the link to your experiment:
                https://paccanarolab.org/s2f_service/job/{token}</p>

                <p>This is a no-reply e-mail and it is not actively monitored,
                please visit https://paccanarolab.org/s2f if you have any
                questions about S2F.</p>

                <p>Kind Regards,</p>

                <p>S2F Team @ PaccanaroLab</p>
            </body>
        </html>"""
    },
    "experiment_started": {
        "subject": "S2F - Experiment Started",
        "body": """<html>
            <head></head>
            <body>
                <h1>Experiment Successfully Registered</h1>

                <p>Thanks for using the S2F prediction service,</p>

                <p>Your job {alias}, started running on {date}.
                Below, you can find a link to track the progress of the
                experiment, as well as the downloadable results. This link was
                sent in a previous e-mail as well.</p>

                <p>Results are not kept in our servers indefinitely, and will
                be deleted when space is required for other experiments in the
                queue. We can only ensure the files remain in the server for
                24 hours.</p>

                <p>This is the link to your experiment:
                https://paccanarolab.org/s2f_service/job/{token}</p>

                <p>This is a no-reply e-mail and it is not actively monitored,
                please visit https://paccanarolab.org/s2f if you have any
                questions about S2F.</p>

                <p>Kind Regards,</p>

                <p>S2F Team @ PaccanaroLab</p>
            </body>
        </html>"""
    },
    "experiment_finished": {
        "subject": "S2F - Experiment Done",
        "body": """<html>
            <head></head>
            <body>
                <h1>Experiment Successfully Finished</h1>

                <p>Thanks for using the S2F prediction service,</p>

                <p>Your job {alias}, finished running on {date}.
                Below, you can find a link to download the results.
                This link was sent in a previous e-mail as well.</p>

                <p>Results are not kept in our servers indefinitely, and will
                be deleted when space is required for other experiments in the
                queue. We can only ensure the files remain in the server for
                24 hours.</p>

                <p>This is the link to your experiment:
                https://paccanarolab.org/s2f_service/job/{token}</p>

                <p>This is a no-reply e-mail and it is not actively monitored,
                please visit https://paccanarolab.org/s2f if you have any
                questions about S2F.</p>

                <p>Kind Regards,</p>

                <p>S2F Team @ PaccanaroLab</p>
            </body>
        </html>"""
    },
}

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "PaccanaroLab <support@paccanarolab.org>"


# If necessary, replace us-west-2 with the AWS Region you're using for SES.
AWS_REGION = "us-east-1"

# The character encoding for the email.
CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses', region_name=AWS_REGION)


def send_email(recipient, body_html, subject):
    # Try to send the email.
    print(f"Sent [{subject}] email to <{recipient}>")
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': clean_html(body_html),
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
