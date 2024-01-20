import boto3

AWS_DEFAULT_REGION = 'us-east-1'

try:
    session = boto3.Session(
        aws_access_key_id='AKIA3V6C3DMJ7Z2UMCFH',
        aws_secret_access_key='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',
        region_name=AWS_DEFAULT_REGION
    )
    dynamodb_resource = session.resource('dynamodb')
    PAPER_CLAIMS_TABLE = dynamodb_resource.Table('paper-claims')
except Exception as e:
    print(f"Error initializing DynamoDB table: {str(e)}")



