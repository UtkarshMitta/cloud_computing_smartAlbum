import json
import boto3
import requests
import botocore.exceptions


def lambda_handler(event, context):
    print('Event:', event)
    # Extract query text and sessionId from the event
    inputText = event['queryStringParameters']['q']
    print('Input Text:', inputText)
    
    # Get keywords from Lex bot
    keywords = get_keywords(inputText)
    print('Keywords:', keywords)
    
    # Get image locations based on keywords
    image_array = get_image_locations(keywords)
    
    return {
        'statusCode': 200,
        'headers': {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps({"results": image_array})
    }


def get_keywords(input_text):
    client = boto3.client('lexv2-runtime')
    response = client.recognize_text(
        botAliasId="TSTALIASID",
        botId="KDLSBX31XL",
        localeId="en_US",
        text=input_text,
        sessionId='761018873242206'
    )
    print('Response: ',response)
    response=response['interpretations'][0]['intent']['slots']['keyword']['value']['resolvedValues']
    return response


def get_image_locations(keywords):
    # Configure OpenSearch endpoint and request headers
    endpoint = 'https://search-photos-uzrb3scixtjfenq6thuj4jqzna.aos.us-east-1.on.aws/_search'
    headers = {'Content-Type': 'application/json'}
    auth = ('Utkarsh@2002', 'Utkarsh@2002')  # Replace with your OpenSearch credentials

    # Prepare the query for OpenSearch
    prepared_q = [{"match": {"labels": keyword}} for keyword in keywords]
    query = {"query": {"bool": {"should": prepared_q}}}
    
    # Send request to OpenSearch
    response = requests.post(endpoint, auth=auth, headers=headers, data=json.dumps(query))
    response_data = response.json()
    print("OpenSearch response:", response_data)
    
    # Parse image URLs from response
    image_array = []
    for hit in response_data['hits']['hits']:
        objectKey = hit['_source']['objectKey']
        bucket = hit['_source']['bucket']
        image_url = f"https://{bucket}.s3.amazonaws.com/{objectKey}"
        if image_url not in image_array:  # Avoid duplicates
            image_array.append(image_url)
    
    print("Image URLs:", image_array)
    return image_array