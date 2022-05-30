from pandas import read_csv, DataFrame

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_bah_transcript_annotation_and_cpm_cDNA.csv'
GENES_TABLE_PATH: str = 'api/migrations/data/genes.csv'


def main():
    cols_to_include: list = ['gene_id', 'gene_name']
    data: DataFrame = read_csv(RAW_TABLE_PATH, usecols=cols_to_include)
    data: DataFrame = data.drop_duplicates(subset='gene_id')

    assert data['gene_id'].nunique() == len(data)
    assert not any(data['gene_id'].isna())
    assert any(data['gene_name'].isna())

    data.to_csv(GENES_TABLE_PATH, index=False)


if __name__ == '__main__':
    main()
