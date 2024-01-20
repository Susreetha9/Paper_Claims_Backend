import json
import uuid
from decimal import Decimal
from boto3.dynamodb.conditions import Attr, Key
from django.contrib.sites import requests

from .configurations import PAPER_CLAIMS_TABLE
from .common import current_date_time
from django.core.files.storage import FileSystemStorage


class PaperClaimTable:
    def __init__(self, doc_id=None, analyst=None, analyst_comments=None, file_path=None,
                 doc_status=None, doc_metadata=None, doc_type=None,
                 health_plan=None, health_plan_api=None, published_on=None, upload_date=None):
        self.doc_id = doc_id or str(uuid.uuid4())
        self.analyst = analyst
        self.analyst_comments = analyst_comments
        self.file_path = file_path
        self.doc_status = doc_status
        self.doc_metadata = doc_metadata
        self.doc_type = doc_type
        self.health_plan = health_plan
        self.health_plan_api = health_plan_api
        self.published_on = published_on
        self.upload_date = upload_date

    @classmethod
    def store(cls, data):
        # Use the provided doc_id if available, otherwise generate a new UUID
        # data['doc_id'] = data.get('doc_id', str(uuid.uuid4()))

        # Ensure that doc_id, doc_type, and health_plan are present in the data
        if 'doc_id' not in data or 'doc_type' not in data or 'health_plan' not in data:
            raise ValueError("doc_id, doc_type, and health_plan are required attributes.")

        # Create the item dictionary
        item = {
            'doc_id': data['doc_id'],
            'analyst': data.get('analyst', ''),
            'analyst_comments': data.get('analyst_comments', ''),
            'file_path': data.get('file_path', ''),
            'doc_status': data.get('doc_status', ''),
            'doc_metadata': data.get('doc_metadata', ''),
            'doc_type': data['doc_type'],
            'health_plan': data['health_plan'],
            'health_plan_api': data.get('health_plan_api', ''),
            'published_on': data.get('published_on', ''),
            'upload_date': data.get('upload_date', ''),
        }

        # Use the put_item method to store the item in the DynamoDB table
        paper_claim_instance = PAPER_CLAIMS_TABLE.put_item(Item=item)
        return paper_claim_instance

    @classmethod
    def save_uploaded_file(cls, doc_id, uploaded_file):
        # Use the provided doc_id if available, otherwise generate a new UUID
        doc_id = doc_id

        # Initialize the FileSystemStorage
        fs = FileSystemStorage(location='C:/Users/dell/PycharmProjects/Folder')

        # Save the file to your local file system
        file_path = fs.save(f'{doc_id}.pdf', uploaded_file)

        # Later add code to store the file_path in the database or perform additional processing
        return file_path



    @classmethod
    def send_pdf_to_api(cls, doc_id, file_path):
        try:
            # Ensure the file_path is not None or empty
            if not file_path:
                raise ValueError("Invalid file path")

            # Prepare the files dictionary for the other API
            files = {'pdf_file': open(file_path, 'rb')}

            # Add other required parameters
            data = {
                'doc_id': doc_id,
                # Add other parameters if needed
            }

            # Make a request to the other API
            response = requests.post('https://other-api-url.com', data=data, files=files)

            # Check if the request was successful (status code 2xx)
            response.raise_for_status()

            # Process the response as needed
            processed_response = response.json()

            # Optionally, you can further process the JSON response

            return processed_response

        except Exception as e:
            # Log the exception or handle it appropriately
            print(f"Error in send_pdf_to_api: {str(e)}")
            return None

    @classmethod
    def get_by_doc_id(cls, doc_id):
        response = PAPER_CLAIMS_TABLE.get_item(Key={'doc_id': doc_id})
        item = response.get('Item')
        if item:
            return cls(**item)
        return None

    @classmethod
    def get_all(cls):
        response = PAPER_CLAIMS_TABLE.scan()
        return response.get('Items', [])

    @classmethod
    def update_by_id(cls, doc_id, updates):
        update_expr_parts = []
        expr_values = {}
        expr_names = {}

        for key, value in updates.items():
            key_placeholder = f':{key}'
            update_expr_parts.append(f"#{key} = {key_placeholder}")
            expr_values[key_placeholder] = value
            expr_names[f"#{key}"] = key

        update_expression = "SET " + ", ".join(update_expr_parts)

        PAPER_CLAIMS_TABLE.update_item(
            Key={'doc_id': doc_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expr_values,
            ExpressionAttributeNames=expr_names
        )

    @classmethod
    def delete_by_id(cls, doc_id):
        PAPER_CLAIMS_TABLE.delete_item(Key={'doc_id': doc_id})

    @classmethod
    def delete_all(cls):
        response = PAPER_CLAIMS_TABLE.scan()
        for item in response.get('Items', []):
            PAPER_CLAIMS_TABLE.delete_item(Key={'doc_id': item['doc_id']})
