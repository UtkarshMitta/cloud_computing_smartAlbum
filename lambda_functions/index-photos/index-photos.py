import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from datetime import datetime
# This comit is for testing the codepipeline in lambda function
# This should reflect on the lambda instance on AWS

#test
def lambda_handler(event, context):
    try:
        # Initialize OpenSearch client
        print('Event: ',event)
        host = "search-photos-****************.aos.us-east-1.on.aws"
        opensearch = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            use_ssl=True,
            http_auth=('**********', '**********'),
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        # Loop through S3 events
        for record in event['Records']:
            event_name = record['eventName']
            bucket = record['s3']['bucket']['name']
            photo = record['s3']['object']['key']
            print(f"Bucket: {bucket}, Key: {photo}, Event: {event_name}")

            if event_name.startswith("ObjectRemoved"):  # Handle S3 delete event
                print(f"Deleting document for key: {photo} from OpenSearch.")
                # Delete the document from OpenSearch
                delete_response = opensearch.delete(index="photos", id=photo, ignore=[404])
                print(f"Document deleted: {delete_response}")
            
            elif event_name.startswith("ObjectCreated"):  # Handle S3 upload event
                created_timestamp = datetime.utcnow().isoformat() + "Z"
                
                # Initialize AWS clients
                s3_client = boto3.client('s3')
                rekognition_client = boto3.client('rekognition')

                # Fetch image from S3 bucket
                s3_object = s3_client.get_object(Bucket=bucket, Key=photo)
                image_data = s3_object['Body'].read()  # Read as binary directly

                # Retrieve custom labels from metadata
                s3_metadata = s3_client.head_object(Bucket=bucket, Key=photo)
                custom_labels_header = s3_metadata['Metadata'].get('x-amz-meta-customlabels', '')
                custom_labels = [label.strip().lower() for label in custom_labels_header.split(',') if label.strip()]
                for i in range(len(custom_labels)):
                    custom_labels[i]=custom_labels[i].split(',')
                    temp=''
                    for letter in custom_labels[i]:
                        temp+=letter
                    custom_labels[i]=temp
                print(f"Custom Labels: {custom_labels}")
                # Detect labels using Rekognition
                rekognition_response = rekognition_client.detect_labels(
                    Image={'Bytes': image_data},
                    MaxLabels=10,
                    MinConfidence=80
                )
                rekognition_labels = [label['Name'].lower() for label in rekognition_response['Labels']]
                print(f"Rekognition Labels: {rekognition_labels}")

                # Combine Rekognition labels and custom labels
                all_labels = list(set(rekognition_labels + custom_labels))
                print(f"All Labels (combined): {all_labels}")

                # Format data for OpenSearch
                document = {
                    'objectKey': photo,
                    'bucket': bucket,
                    'createdTimestamp': created_timestamp,
                    'labels': all_labels
                }

                # Index the document in OpenSearch
                index_response = opensearch.index(index="photos", id=photo, body=document)
                print(f"Document indexed successfully: {index_response}")

        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "*"
            },
            'body': json.dumps({'message': 'Success'})
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "*"
            },
            'body': json.dumps(f'Error processing event: {str(e)}')
        }
