from django.urls import path

from .views import process_pdf

urlpatterns = [
    path('claims_extraction/', process_pdf, name='process_pdf')
]
