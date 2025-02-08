import json
import boto3
import requests
import botocore.exceptions

"""
Testing codepipeline for our assignment
should reflect on search-photos
"""
def lambda_handler(event, context):
    try:
        print('Event:', event)
        # Extract query text and sessionId from the event
        inputText = None
        if 'inputTranscript' in event:
            inputText=event['inputTranscript']
        else:
            inputText=event['queryStringParameters']['q']
        print('Input Text:', inputText)
        
        # Get keywords from Lex bot
        keywords = get_keywords(inputText)
        if (keywords == ""):
            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
                },
                'body': json.dumps({"results": [],
                                    "error": "Unable to retrieve keywords.."})
            }
        
        keywords = keywords.split(',')

        
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
    except Exception as e:
        print('Error occurred:', e)
        return {
            'statusCode': 500,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': json.dumps({"results": [],
                                "error": str(e)})
        }


def get_keywords(input_text):
    client = boto3.client('lexv2-runtime')
    response = client.recognize_text(
        botAliasId="TSTALIASID",
        botId="KDLSBX31XL",
        localeId="en_US",
        text=input_text,
        sessionId='761018873242296'
    )
    
    print('Response: ',response)
    
    if (response.get('messages', '') == ''):
        return ""

    return response['messages'][0]['content']




def get_image_locations(keywords):
    # Configure OpenSearch endpoint and request headers
    endpoint = 'https://search-photos-***************.aos.us-east-1.on.aws/_search'
    headers = {'Content-Type': 'application/json'}
    auth = ('************', '***********')  # Replace with your OpenSearch credentials

    # Prepare the query for OpenSearch
    prepared_q = [{"match": {"labels": keyword}} for keyword in keywords]
    print('prepared_q: ', prepared_q)

    query = {"query": {"bool": {"should": prepared_q}}}
    
    # Send request to OpenSearch
    response = requests.post(endpoint, auth=auth, headers=headers, data=json.dumps(query))
    print('Response0: ',response)
    response_data = response.json()
    print("OpenSearch response:", response_data)
    
    # Parse image URLs from response
    image_array = []
    unique_urls = set()
    for hit in response_data['hits']['hits']:
        objectKey = hit['_source']['objectKey']
        bucket = hit['_source']['bucket']
        max_labels = len(hit['_source']['labels'])
        image_labels = []
        if (max_labels > 2):
            image_labels = hit['_source']['labels'][:2]
        else:
            image_labels = hit['_source']['labels']
        #print ("image_labels", image_labels)
        #print (hit['_source']['objectKey'])
        
        image_title = hit['_source']['objectKey']
        image_url = f"https://{bucket}.s3.amazonaws.com/{objectKey}"

        if (image_url not in unique_urls):
            image_array.append({
                "URL": image_url,
                "Labels": image_labels,
                "Title": image_title
            })

        unique_urls.add(image_url)
    
    print("Image URLs:", image_array)
    return image_array
