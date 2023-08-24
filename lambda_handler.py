# Mailchimp not working, edit campaign
# To section incomplete- MC is mail lists, can't send one email and not bug them again.
# Content section might be wrong, |DYNAMIC_CONTENT| does not appear to be a valid mergefield

import json
import requests
import os

OPENAI_KEY = os.environ["OPENAI_KEY"]
MANDRILL_API_KEY = os.environ["MANDRILL_API_KEY"]


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

    # Mandrill API call to send the email
    mandrill_url = "https://mandrillapp.com/api/1.0/messages/send.json"
    headers_mandrill = {
        "Content-Type": "application/json",
    }
    payload_mandrill = {
        "key": MANDRILL_API_KEY,
        "message": {
            "html": chatgpt_content,
            "subject": "Discover the Power of AI for Your Business",
            "from_email": "your_email@gopurple.ai",  # Replace with your Mandrill verified email
            "from_name": "Brooks from Purple AI",
            "to": [{"email": email, "type": "to"}],
        },
    }

    response = requests.post(
        mandrill_url, json=payload_mandrill, headers=headers_mandrill
    )
    mandrill_response = response.json()

    # Check the Mandrill response for success or errors
    if mandrill_response[0].get("status") == "sent":
        return {
            "statusCode": 200,
            "body": "Email content generated and sent via Mandrill.",
        }
    else:
        # Log the Mandrill error for debugging
        print("Mandrill Response:", mandrill_response)
        return {
            "statusCode": 400,
            "body": f"Failed to send email via Mandrill: {mandrill_response[0].get('reject_reason', 'Unknown error')}",
        }
