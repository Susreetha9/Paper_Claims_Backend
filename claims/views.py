import io
import boto3
import uuid
from pdf2image import convert_from_bytes
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

AWS_DEFAULT_REGION = 'us-east-1'

session = boto3.Session(
    aws_access_key_id='AKIA3V6C3DMJ7Z2UMCFH',
    aws_secret_access_key='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',
    region_name=AWS_DEFAULT_REGION
)

poppler_path = 'C:\\Users\\Lakshmi Susreetha\\poppler-23.11.0\\Library\\bin'
os.environ["PATH"] += os.pathsep + poppler_path

@csrf_exempt
def process_pdf(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return JsonResponse({'error': 'No PDF file provided'}, status=400)

        images = convert_from_bytes(pdf_file.read())

        textract = boto3.client('textract')

        results = []
        for image in images:
            image_bytes = convert_image_to_bytes(image)
            response = textract.analyze_document(
                Document={'Bytes': image_bytes},
                FeatureTypes=["FORMS", "TABLES"]
            )
            processed_data = process_textract_response(response)
            results.append(processed_data)

        return JsonResponse({'results': results})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def convert_image_to_bytes(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def process_textract_response(response):
    raw_text = extract_text(response, extract_by="LINE")
    word_map = map_word_id(response)
    table_info = extract_table_info(response, word_map)
    key_map = get_key_map(response, word_map)
    value_map = get_value_map(response, word_map)
    final_map = get_kv_map(key_map, value_map)

    return {
        'RawText': raw_text,
        'Tables': table_info,
        'FormKeyValues': final_map
    }


def extract_text(response, extract_by="WORD"):
    line_text = []
    for block in response["Blocks"]:
        if block["BlockType"] == extract_by:
            line_text.append(block["Text"])
    return line_text


def map_word_id(response):
    word_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "WORD":
            word_map[block["Id"]] = block["Text"]
        if block["BlockType"] == "SELECTION_ELEMENT":
            word_map[block["Id"]] = block["SelectionStatus"]
    return word_map

def extract_table_info(response, word_map):
    row = []
    table = {}
    ri = 0
    flag = False

    for block in response["Blocks"]:
        if block["BlockType"] == "TABLE":
            key = f"table_{uuid.uuid4().hex}"
            table_n = +1
            temp_table = []

        if block["BlockType"] == "CELL":
            if block["RowIndex"] != ri:
                flag = True
                row = []
                ri = block["RowIndex"]

            if "Relationships" in block:
                for relation in block["Relationships"]:
                    if relation["Type"] == "CHILD":
                        row.append(" ".join([word_map[i] for i in relation["Ids"]]))
            else:
                row.append(" ")

            if flag:
                temp_table.append(row)
                table[key] = temp_table
                flag = False
    return table


def get_key_map(response, word_map):
    key_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "KEY" in block["EntityTypes"]:
            for relation in block["Relationships"]:
                if relation["Type"] == "VALUE":
                    value_id = relation["Ids"]
                if relation["Type"] == "CHILD":
                    v = " ".join([word_map[i] for i in relation["Ids"]])
                    key_map[v] = value_id
    return key_map


def get_value_map(response, word_map):
    value_map = {}
    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "VALUE" in block["EntityTypes"]:
            if "Relationships" in block:
                for relation in block["Relationships"]:
                    if relation["Type"] == "CHILD":
                        v = " ".join([word_map[i] for i in relation["Ids"]])
                        value_map[block["Id"]] = v
            else:
                value_map[block["Id"]] = "VALUE_NOT_FOUND"

    return value_map


def get_kv_map(key_map, value_map):
    final_map = {}
    for i, j in key_map.items():
        final_map[i] = "".join(["".join(value_map[k]) for k in j])
    return final_map
