from pandas import DataFrame, read_csv
from numpy import isnan
from tqdm import tqdm

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_coverage_table_for_cDNA_website.csv'
COVERAGES_TABLE_PATH: str = 'api/migrations/data/coverages.csv'


def main():
    new_data: DataFrame = DataFrame(
        {
            'gene_id': [],
            'down_sample_percent': [],
            'illumina_average_coverage': [],
            'nanopore_average_coverage': []
        }
    )

    raw_coverage_table: DataFrame = read_csv(RAW_TABLE_PATH)
    illumina_average_coverage_cols: list = [col for col in raw_coverage_table.columns if 'illumina' in col]
    nanopore_average_coverage_cols: list = [col for col in raw_coverage_table.columns if 'nanopore' in col]

    for _, row in tqdm(raw_coverage_table.iterrows()):
        gene_id: str = row['gene_id']

        assert type(gene_id) is str

        for illumina_average_coverage_col, nanopore_average_coverage_col in zip(
            illumina_average_coverage_cols, nanopore_average_coverage_cols
        ):
            illumina_down_sample_percent: float = float(illumina_average_coverage_col.split('_')[-1])
            nanopore_down_sample_percent: float = float(nanopore_average_coverage_col.split('_')[-1])

            assert illumina_down_sample_percent == nanopore_down_sample_percent

            down_sample_percent: float = illumina_down_sample_percent
            illumina_average_coverage: float = float(row[illumina_average_coverage_col])
            nanopore_average_coverage: float = float(row[nanopore_average_coverage_col])

            new_data.loc[len(new_data)] = [
                gene_id, down_sample_percent, illumina_average_coverage, nanopore_average_coverage
            ]

    new_data.to_csv(COVERAGES_TABLE_PATH, index=False)


if __name__ == '__main__':
    main()

