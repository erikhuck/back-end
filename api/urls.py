from django.urls import path
from django.http import JsonResponse
from . import endpoints


def health_check(_) -> JsonResponse:
    return JsonResponse({})


urlpatterns = [
    path('ht/', health_check, name='health_check'),
    path('gene-coverage/', endpoints.gene_coverage, name='gene_coverage'),
    path('isoforms-expression/', endpoints.isoforms_expression, name='isoforms_expression'),
    path('isoform-exons/', endpoints.isoform_exons, name='isoform_exons'),
    path('genes/', endpoints.genes, name='genes')
]
