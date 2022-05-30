from django.http import JsonResponse, QueryDict

from .utils import get_transcripts_of_gene, get_gene_from_request, get_transcript_info
from api.models import ExpressionLevel


def isoforms_expression(request) -> JsonResponse:
    gene: str = get_gene_from_request(request=request)
    isoform_expression_data: list = _get_isoform_expression_data(gene=gene)

    return JsonResponse(isoform_expression_data)


def _get_isoform_expression_data(gene: str) -> dict:
    transcript_expression_levels: list = []
    gene_name, gene_id, transcripts_of_gene = get_transcripts_of_gene(gene=gene)

    for transcript_of_gene in transcripts_of_gene:
        transcript_name, transcript_id, expression_levels = get_transcript_info(
            transcript=transcript_of_gene, ModelClass=ExpressionLevel
        )

        expression_levels: list = [
            expression_level.expression_level for expression_level in expression_levels
        ]

        transcript_expression_levels.append({
            'isoformName': transcript_name,
            'isoformId': transcript_id,
            'y': expression_levels
        })

    return {
        'geneName': gene_name,
        'geneId': gene_id,
        'isoformExpressions': transcript_expression_levels
    }
