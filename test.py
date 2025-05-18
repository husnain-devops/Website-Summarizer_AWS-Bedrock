import boto3
import json

# Initialize the Bedrock Runtime client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='eu-north-1'
)

try:
    # Test message
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you confirm you're working?"
            }
        ]
    }

    # Make the request
    response = bedrock.invoke_model(
        modelId='eu.anthropic.claude-3-7-sonnet-20250219-v1:0',
        body=json.dumps(body)
    )
    
    # Parse and print the response
    response_body = json.loads(response['body'].read())
    print("Response:", response_body)

except Exception as e:
    print("Error:", str(e))