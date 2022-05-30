from django.http import JsonResponse, QueryDict

from .utils import get_transcripts_of_gene, get_gene_from_request, get_transcript_info
from api.models import TranscriptExon, DnaExon


def isoform_exons(request) -> JsonResponse:
    gene: str = get_gene_from_request(request=request)
    isoform_exon_data: dict = _get_isoform_exon_data(gene=gene)

    return JsonResponse(isoform_exon_data)


def _get_isoform_exon_data(gene: str) -> dict:
    isoforms: list = []
    gene_name, gene_id, transcripts_of_gene = get_transcripts_of_gene(gene=gene)

    for transcript_of_gene in transcripts_of_gene:
        transcript_name, transcript_id, transcript_exons = get_transcript_info(
            transcript=transcript_of_gene, ModelClass=TranscriptExon
        )

        isoform_exon_info: list = []

        for transcript_exon in transcript_exons:
            isoform_exon_info.append({
                'start': transcript_exon.start,
                'end': transcript_exon.end,
                'exonRegionType': transcript_exon.exon_region_type,
                'intronRegionType': transcript_exon.intron_region_type,
                'intronEnd': transcript_exon.intron_end
            })

        isoforms.append({
            'isoformName': transcript_name,
            'isoformId': transcript_id,
            'isoformExonInfo': isoform_exon_info
        })

    return {
        'geneName': gene_name,
        'geneId': gene_id,
        'dnaExonInfo': _get_dna_exon_info(gene_id=gene_id),
        'isoforms': isoforms
    }


def _get_dna_exon_info(gene_id: str) -> list:
    dna_exons = DnaExon.objects.filter(gene_id=gene_id)
    dna_exon_info: list = []

    for dna_exon in dna_exons:
        dna_exon_info.append({
            'start': dna_exon.start,
            'end': dna_exon.end,
            'intronEnd': dna_exon.intron_end
        })

    return dna_exon_info
