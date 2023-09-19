import json
import requests
import os
import boto3
from datetime import datetime, timedelta

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EmailBatchTracking')

# Mailchimp Transactional API configurations
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY')
MAILCHIMP_LIST_ID = os.environ.get('MAILCHIMP_LIST_ID')  # Replace with your Audience/List ID
MAILCHIMP_ENDPOINT = f'https://us12.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members'
MANDRILL_API_KEY = os.environ.get('MANDRILL_API_KEY')
API_URL = 'https://mandrillapp.com/api/1.0/messages/send-template.json'
TEMPLATE_NAME = 'email3'

def lambda_handler(event, context):
    for record in event['Records']:
        # Extracting details from the SQS event
        sqs_message = record['body']
        sqs_data = json.loads(sqs_message)
        email = sqs_data.get('email', '')
        name = sqs_data.get('name', '')

        # Generate a tag based on current time
        current_time = datetime.utcnow()
        tag = current_time.strftime('%Y-%m-%d-%H-%M')

        # Add the email to Mailchimp audience with the current tag
        headers = {
            'Authorization': f'Bearer {MAILCHIMP_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": name.split(' ')[0],
                "LNAME": " ".join(name.split(' ')[1:])
            },
            "tags": [tag]
        }
        response = requests.post(MAILCHIMP_ENDPOINT, headers=headers, json=data)
        if response.status_code != 200:
            print("Error adding member to Mailchimp:", response.text)

        # Send the email without checking the delay
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
        print("Mandrill response:", response.text)


    return {"statusCode": 200, "body": json.dumps('Emails sent successfully!')}
