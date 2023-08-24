import json
import requests
import os
import boto3

OPENAI_KEY = os.environ["OPENAI_KEY"]
ses_client = boto3.client("ses", region_name="us-east-2")


def lambda_handler(event, context):
    # Retrieve JSON data from the event
    json_data = json.loads(event["Records"][0]["body"])

    # Extract necessary information from the JSON data (business name, email, web content)
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
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": chatgpt_prompt},
        ],
    }

    response = requests.post(chatgpt_url, json=payload, headers=headers_openai)
    openai_response = response.json()
    print("ChatGPT Response:", openai_response)

    try:
        composed_email = openai_response["choices"][0]["message"]["content"]
        print("Composed Email:", composed_email)

        # Send email using SES
        response = ses_client.send_email(
            Source="justin@gopurple.ai",  # Replace with your verified email
            Destination={
                "ToAddresses": [
                    email,  # The business's email address
                ],
            },
            Message={
                "Subject": {
                    "Data": "Discover the Power of AI for Your Business",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Text": {
                        "Data": composed_email,
                        "Charset": "UTF-8",
                    },
                },
            },
        )
    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "body": json.dumps("Error occurred while processing."),
        }

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Email composition and sending process triggered successfully"
        ),
    }
