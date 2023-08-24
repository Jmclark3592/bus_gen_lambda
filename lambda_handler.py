# Mailchimp not working, edit campaign
# To section incomplete- MC is mail lists, can't send one email and not bug them again.
# Content section might be wrong, |DYNAMIC_CONTENT| does not appear to be a valid mergefield

import json
import requests
import os

OPENAI_KEY = os.environ["OPENAI_KEY"]
MAILCHIMP_API_KEY = os.environ["MAILCHIMP_API_KEY"]
MAILCHIMP_LIST_ID = os.environ["MAILCHIMP_LIST_ID"]
MAILCHIMP_DATA_CENTER = "us12"
MAILCHIMP_CAMPAIGN_ID = "1084706"


def lambda_handler(event, context):
    # Extract company info from the SQS message
    json_data = json.loads(event["Records"][0]["body"])
    business_name = json_data.get("name")
    email = json_data.get("email")
    web_content = json_data.get("web_content")

    # Generate email content using ChatGPT
    chatgpt_url = "https://api.openai.com/v1/chat/completions"
    headers_openai = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}",
    }
    chatgpt_prompt = (
        f"Hello Assistant, I want to provide you with some context first. I am Brooks, owner of Purple AI. Our company specializes in:"
        f"\n- Expert training in AI technologies."
        f"\n- Strategic business insights through AI."
        f"\n- Driving product and process innovation using AI."
        f"\n\nOur mission is to integrate AI technologies into business workflows, redefine strategies, and foster innovation. "
        f"\n\nNow, I've come across a company named {business_name}. Here's some information about them from their website: \n\n{web_content}"
        f"\n\nBased on this information about {business_name}, can you help me craft a concise email offering Purple AI's services to them, highlighting how we can benefit them specifically?"
        f"\n\nPlease address the email to the {business_name} team."
    )

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": chatgpt_prompt},
        ],
    }

    response = requests.post(chatgpt_url, json=payload, headers=headers_openai)
    openai_response = response.json()
    print("OpenAI Response:", openai_response)

    try:
        chatgpt_content = openai_response["choices"][0]["message"]["content"]
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps("Failed to generate content from OpenAI"),
        }

    print("Preparing to call Mailchimp with content:", chatgpt_content)

    # Mailchimp API call to add the contact
    mailchimp_url = f"https://{MAILCHIMP_DATA_CENTER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
    headers_mailchimp = {
        "Authorization": f"Bearer {MAILCHIMP_API_KEY}",
        "Content-Type": "application/json",
    }
    payload_mailchimp = {
        "email_address": email,
        "status": "subscribed",
        "merge_fields": {"DYNAMIC_CONTENT": chatgpt_content},
    }

    response = requests.post(
        mailchimp_url, json=payload_mailchimp, headers=headers_mailchimp
    )
    mailchimp_response = response.json()

    # Check the Mailchimp response for success or errors
    if response.status_code == 200:
        return {
            "statusCode": 200,
            "body": "Email content generated and contact added to Mailchimp.",
        }
    else:
        # Log the Mailchimp error for debugging
        print("Mailchimp Response:", mailchimp_response)
        return {
            "statusCode": 400,
            "body": f"Failed to add/update contact in Mailchimp: {mailchimp_response.get('detail', 'Unknown error')}",
        }
