from django.http import JsonResponse
from api.models import Gene


def genes(_) -> JsonResponse:
    gene_names: list = _get_distinct_values(col_name='gene_name')
    gene_ids: list = _get_distinct_values(col_name='gene_id')
    all_genes = gene_names + gene_ids

    return JsonResponse(all_genes, safe=False)


def _get_distinct_values(col_name: str) -> list:
    query = Gene.objects.values(col_name).distinct()
    distinct_values: list = []

    for distinct_value in query:
        distinct_value: str = distinct_value[col_name]

        assert distinct_value != ''

        if distinct_value is not None:
            distinct_values.append({'label': distinct_value})

    return distinct_values
