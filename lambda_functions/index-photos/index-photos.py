import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
import base64
import time
from datetime import datetime

def lambda_handler(event, context):
    # Get S3 event details
    bucket = event['Records'][0]['s3']['bucket']['name']
    photo = event['Records'][0]['s3']['object']['key']
    print(f"Bucket: {bucket}, Key: {photo}")
    
    createdTimestamp = datetime.utcfromtimestamp(time.time()).isoformat() + "Z"
    
    # Initialize AWS clients
    s3_client = boto3.client('s3')
    rekognition_client = boto3.client('rekognition')

    try:
        # Fetch image from S3 bucket
        s3_object = s3_client.get_object(Bucket=bucket, Key=photo)
        image_data = s3_object['Body'].read()  # Read as binary directly

        # Retrieve custom labels from metadata
        s3_metadata = s3_client.head_object(Bucket=bucket, Key=photo)
        custom_labels_header = s3_metadata['Metadata'].get('customlabels', '')
        print(f"Custom Labels Header: {custom_labels_header}")
        custom_labels=custom_labels_header.split(',,,')
        print(f"Custom Labels: {custom_labels}")
        for i in range(len(custom_labels)):

            temp_list=[letter for letter in custom_labels[i].split(',')]
            temp_str=''
            for letter in temp_list:
                temp_str+=letter
            custom_labels[i]=temp_str
        print(f"Custom Labels: {custom_labels}")
        # Detect labels using Rekognition
        rekognition_response = rekognition_client.detect_labels(
            Image={'Bytes': image_data},
            MaxLabels=10,
            MinConfidence=80
        )

        # Collect Rekognition labels
        rekognition_labels = [label['Name'].lower() for label in rekognition_response['Labels']]
        print(f"Rekognition Labels: {rekognition_labels}")
        
        # Combine Rekognition labels and custom labels
        all_labels = list(set(rekognition_labels + custom_labels))  # Combine and remove duplicates
        print(f"All Labels (combined): {all_labels}")

        # Format data for OpenSearch
        document = {
            'objectKey': photo,
            'bucket': bucket,
            'createdTimestamp': createdTimestamp,
            'labels': all_labels
        }

        # Initialize OpenSearch client
        host = "search-photos-uzrb3scixtjfenq6thuj4jqzna.aos.us-east-1.on.aws"
        opensearch = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            use_ssl=True,
            http_auth=('Utkarsh@2002', 'Utkarsh@2002'),
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        # Index the document in OpenSearch
        response = opensearch.index(index='photos', body=document)
        print(f"Document indexed successfully: {response}")

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': json.dumps({'message': 'Success'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing photo: {str(e)}')
        }