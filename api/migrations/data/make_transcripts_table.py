from pandas import read_csv, DataFrame

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_bah_transcript_annotation_and_cpm_cDNA.csv'
TRANSCRIPTS_TABLE_PATH: str = 'api/migrations/data/transcripts.csv'


def main():
    cols_to_include: list = ['transcript_id', 'transcript_name', 'gene_id']
    data: DataFrame = read_csv(RAW_TABLE_PATH, usecols=cols_to_include)

    assert data['transcript_id'].nunique() == len(data)
    assert not any(data['transcript_id'].isna())
    assert any(data['transcript_name'].isna())
    assert not any(data['gene_id'].isna())
    assert data['gene_id'].nunique() < len(data)

    data.to_csv(TRANSCRIPTS_TABLE_PATH, index=False)


if __name__ == '__main__':
    main()
