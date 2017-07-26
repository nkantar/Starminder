import boto3
import parsenvy


AWS_ACCESS_KEY_ID = parsenvy.str('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = parsenvy.str('AWS_SECRET_ACCESS_KEY')


def send_email(email, subject, text, html):
    b3 = boto3.client('ses',
                      region_name='us-east-1',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    email_kwargs = {
        'Source': 'Starminder <notifications@starminder.xyz>',
        'Destination': {
            'ToAddresses': [
                email
            ],
        },
        'Message': {
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': text
                },
                'Html': {
                    'Data': html
                }
            }
        },
        'ReplyToAddresses': [
            'nik+starminder@nkantar.com'
        ]
    }

    response = b3.send_email(**email_kwargs)
    return response
