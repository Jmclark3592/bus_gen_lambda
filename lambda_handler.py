import json
import requests
import os

def send_email(event, context):
    # Extracting details from the SQS event
    sqs_message = event['Records'][0]['body']
    sqs_data = json.loads(sqs_message)
    email = sqs_data.get('email', '')
    name = sqs_data.get('name', '')

    # Mailchimp Transactional API configurations
    MANDRILL_API_KEY = os.environ.get('MANDRILL_API_KEY')
    API_URL = 'https://mandrillapp.com/api/1.0/messages/send-template.json'
    TEMPLATE_NAME = 'survey2'

    # Constructing the API payload
    payload = {
        "key": MANDRILL_API_KEY,
        "template_name": TEMPLATE_NAME,
        "template_content": [],
        "message": {
            "from_email": "brooks@gopurple.ai",
            "from_name": "Brooks",
            "to": [
                {
                    "email": email,
                    "name": name,
                    "type": "to"
                }
            ],
            "subject": "Discover the Power of AI for Your Business",
            "global_merge_vars": [
                {
                    "name": "BUSINESSNAME",
                    "content": name
                }
            ]
        }
    }

    # Sending the email
    response = requests.post(API_URL, data=json.dumps(payload))
    return response.json()
