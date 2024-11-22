import json
import base64
import boto3
import uuid

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    print('Event:', event)

    try:
        # Extract custom labels from headers (comma-separated string)
        custom_labels_header = event['headers'].get('x-amz-meta-customlabels', '')

        # Parse the request body
        body = json.loads(event['body'])

        # Extract image data and filename
        image_data = body['imageData']  # Base64-encoded image string
        file_name = body['filename']   # Desired filename
        bucket_name = 'assign3-photos' # S3 bucket name

        # Decode the Base64 string into image bytes
        image_bytes = base64.b64decode(image_data)

        # Generate a unique filename if none is provided
        if not file_name:
            file_name = f"image-{uuid.uuid4()}.png"

        # Upload the image to the S3 bucket with metadata
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_bytes,
            ContentType='image/png',  # Adjust based on your image type
            Metadata={
                'customlabels': ','.join(custom_labels_header)  # Store the labels as a comma-separated string
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Or replace '*' with the specific domain
                "Access-Control-Allow-Methods": "GET, PUT, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, x-amz-meta-customLabels"
            },
            "body": json.dumps({
                "message": "Image uploaded successfully"
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",  # Or replace '*' with the specific domain
                "Access-Control-Allow-Methods": "GET, PUT, POST, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({
                "message": "Failed to upload image"
            })
        }