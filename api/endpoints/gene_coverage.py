from django.http import JsonResponse

from api.models import Coverage
from .utils import get_gene_from_request, query_by_gene

AVG_TOTAL_NUM_READS_ILLUMINA: int = 46
AVG_TOTAL_NUM_READS_NANOPORE: int = 49


def gene_coverage(request) -> JsonResponse:
    gene: str = get_gene_from_request(request=request)
    coverage_data: dict = _get_coverage_data(gene=gene)

    return JsonResponse(coverage_data)


def _get_coverage_data(gene: str) -> dict:
    gene_name, gene_id, coverages = query_by_gene(gene=gene, ModelClass=Coverage)
    down_sample_percents: list = [coverage.down_sample_percent for coverage in coverages]

    illumina_down_sampled_reads: dict = _get_down_sampled_reads(
        avg_total_num_reads=AVG_TOTAL_NUM_READS_ILLUMINA, down_sample_percents=down_sample_percents
    )

    nanopore_down_sampled_reads: dict = _get_down_sampled_reads(
        avg_total_num_reads=AVG_TOTAL_NUM_READS_NANOPORE, down_sample_percents=down_sample_percents
    )

    illumina_coverage_data: dict = {}
    nanopore_coverage_data: dict = {}

    for coverage in coverages:
        down_sample_percent: float = coverage.down_sample_percent
        illumina_down_sampled_read: float = illumina_down_sampled_reads[down_sample_percent]
        nanopore_down_sampled_read: float = nanopore_down_sampled_reads[down_sample_percent]
        illumina_coverage_data[illumina_down_sampled_read] = coverage.illumina_average_coverage
        nanopore_coverage_data[nanopore_down_sampled_read] = coverage.nanopore_average_coverage

    return {
        'geneName': gene_name,
        'geneId': gene_id,
        'illuminaCoverageData': illumina_coverage_data,
        'nanoporeCoverageData': nanopore_coverage_data
    }


def _get_down_sampled_reads(avg_total_num_reads: int, down_sample_percents: list) -> dict:
    reads: dict = {}

    # Iterate through down-sampling ranges
    for down_sample_percent in down_sample_percents:
        current_num_reads: float = round(avg_total_num_reads * down_sample_percent, 0)
        reads[down_sample_percent] = current_num_reads

    return reads
