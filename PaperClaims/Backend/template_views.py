import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .configurations import MASTER_TABLE
from .template_models import PaperClaimTable, MasterTable


@csrf_exempt
def store_document_info(request):
    if request.method == 'POST':
        try:
            doc_id = request.POST.get('doc_id')
            doc_type = request.POST.get('doc_type')
            health_plan = request.POST.get('health_plan')
            uploaded_file = request.FILES.get('pdf_file')

            if not doc_id or not doc_type or not health_plan or not uploaded_file:
                return JsonResponse({'error': 'Missing required parameters'}, status=400)

            # Save the file locally
            file_path = PaperClaimTable.save_uploaded_file(doc_id, uploaded_file)

            # Store document information in DynamoDB
            paper_claim_instance = PaperClaimTable.store({
                'doc_id': doc_id,
                'doc_type': doc_type,
                'health_plan': health_plan,

            })

            # Send PDF to the other API
            response_from_other_api = PaperClaimTable.send_pdf_to_api(doc_id, file_path)

            return JsonResponse({
                'message': 'Document information stored successfully',
                'response_from_other_api': response_from_other_api,
            })


        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_paper_claims(request, doc_id):
    if request.method == 'GET':
        paper_claims_data = PaperClaimTable.get(doc_id)
        if paper_claims_data:
            return JsonResponse({'data': paper_claims_data})
        else:
            return JsonResponse({'message': 'Data not found'}, status=404)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_all_paper_claims(request):
    if request.method == 'GET':
        paper_claims_data = PaperClaimTable.get_all()
        return JsonResponse({'data': paper_claims_data})
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def update_paper_claims(request, doc_id):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            PaperClaimTable.update_by_id(doc_id, data)
            return JsonResponse({'message': 'Updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def delete_paper_claims(request, doc_id):
    if request.method == 'DELETE':
        try:
            PaperClaimTable.delete_by_id(doc_id)
            return JsonResponse({'message': 'Deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def delete_all_paper_claims(request):
    if request.method == 'DELETE':
        try:
            PaperClaimTable.delete_all()
            return JsonResponse({'message': 'All data deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)


@csrf_exempt
def master_table_api(request):
    if request.method == 'GET':
        try:
            # Retrieve distinct values for doc_type and health_plan from the master-table
            doc_types = MasterTable.get_distinct_values('doc_type')
            health_plans = MasterTable.get_distinct_values('health_plan')

            # Return JSON response
            return JsonResponse({
                'doc_types': doc_types,
                'health_plans': health_plans
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)

