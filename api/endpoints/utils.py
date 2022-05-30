from django.http import Http404
from django.core.exceptions import BadRequest

from api.models import Transcript, Gene


def get_gene_from_request(request) -> str:
    query_params: QueryDict = request.GET
    gene: str = query_params['gene']

    return gene


def get_transcripts_of_gene(gene: str) -> tuple:
    return query_by_gene(gene=gene, ModelClass=Transcript)


def query_by_gene(gene: str, ModelClass: type) -> tuple:
    if gene == '':
        raise BadRequest

    gene_ids = Gene.objects.filter(gene_id=gene)
    gene_names = Gene.objects.filter(gene_name=gene)

    if len(gene_ids) == 1:
        gene: Gene = gene_ids.first()
    elif len(gene_names) == 1:
        gene: Gene = gene_names.first()
    else:
        raise Http404

    gene_id: str = gene.gene_id
    gene_name: str = gene.gene_name

    rows = ModelClass.objects.filter(gene_id=gene_id)

    return gene_name, gene_id, rows


def get_transcript_info(transcript: Transcript, ModelClass: type) -> tuple:
    transcript_id: str = transcript.transcript_id
    transcript_name: str = transcript.transcript_name
    objects = ModelClass.objects.filter(transcript__transcript_id=transcript_id)

    return transcript_name, transcript_id, objects
