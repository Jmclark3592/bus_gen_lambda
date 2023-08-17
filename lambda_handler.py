import json
import boto3
import requests


def lambda_handler(event, context):
    # Retrieve JSON data from the event
    json_data = json.loads(event["Records"][0]["body"])

    # Extract necessary information from the JSON data (business name, email, web content)
    business_name = json_data.get("name")
    email = json_data.get("email")
    web_content = json_data.get("web_content")

    # TODO: Interact with ChatGPT API to compose an email based on web content
    # Use the necessary prompts and instructions for ChatGPT
    chatgpt_api_key = "YOUR_OPENAI_API_KEY"
    chatgpt_prompt = f"Compose an email for {business_name} based on the following web content:\n\n{web_content}."
    chatgpt_url = "https://api.openai.com/v1/engines/davinci/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {chatgpt_api_key}",
    }

    payload = {"prompt": chatgpt_prompt, "temperature": 0.7, "max_tokens": 100}

    response = requests.post(chatgpt_url, json=payload, headers=headers)
    chatgpt_response = response.json()
    composed_email = chatgpt_response["choices"][0]["text"]

    # TODO: Trigger the email sending process using Zapier or another Lambda function
    # For now, let's just print the composed email
    print("Composed Email:")
    print(composed_email)

    return {
        "statusCode": 200,
        "body": json.dumps(
            "Email composition and sending process triggered successfully"
        ),
    }
