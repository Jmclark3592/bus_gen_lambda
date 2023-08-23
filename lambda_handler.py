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

    # Use the new explicit prompt for ChatGPT
    chatgpt_prompt = (
        f"Craft a professional email for {business_name} where we offer our services. "
        f"We specialize in helping businesses leverage AI to redefine their strategy. "
        f"Highlight the advantages of integrating AI into their existing operations, "
        f"and how it can revolutionize their business model. Use the following content for reference:\n\n{web_content}"
    )

    chatgpt_url = "https://api.openai.com/v1/engines/davinci/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}",
    }

    payload = {
        "prompt": chatgpt_prompt,
        "temperature": 0.5,
        "max_tokens": 500,
    }

    response = requests.post(chatgpt_url, json=payload, headers=headers)
    chatgpt_response = response.json()

    # Print the entire ChatGPT response for debugging
    print("ChatGPT Response:")
    print(json.dumps(chatgpt_response, indent=2))

    # Attempt to retrieve composed email text
    try:
        composed_email = chatgpt_response["choices"][0]["text"]
        print("Composed Email:")
        print(composed_email)

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

    except KeyError as e:
        print("Error retrieving composed email:", e)

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Email composition and sending process triggered successfully"
        ),
    }
