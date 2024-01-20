from . import template_views
from django.urls import path

from .template_views import store_document_info, get_all_paper_claims, get_paper_claims, update_paper_claims, \
    delete_paper_claims, delete_all_paper_claims, master_table_api

urlpatterns = [
    path('store_document_info/', store_document_info, name='store_document_info'),
    path('get_paper_claim/<str:doc_id>/', get_paper_claims, name='get_paper_claim'),
    path('get_all_paper_claim/', get_all_paper_claims, name='get_all_paper_claim'),
    path('update_paper_claim/<str:doc_id>/', update_paper_claims, name='update_paper_claim'),
    path('delete_paper_claim/<str:doc_id>/', delete_paper_claims, name='delete_paper_claim'),
    path('delete_all_paper_claim/', delete_all_paper_claims, name='delete_all_paper_claim'),
    path('api/master-table/', master_table_api, name='master_table_api'),

]
