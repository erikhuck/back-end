from pandas import DataFrame, read_csv, Series
from tqdm import tqdm

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_bah_merged_exons_cDNA.csv'
DNA_EXONS_TABLE_PATH: str = 'api/migrations/data/dna_exons.csv'


def main():
    cols_to_include: list = ['gene_id', 'start', 'end']
    raw_data: DataFrame = read_csv(RAW_TABLE_PATH, usecols=cols_to_include)

    assert raw_data['gene_id'].nunique() < len(raw_data)
    assert not any(raw_data['gene_id'].isna())
    assert not any(raw_data['start'].isna())
    assert not any(raw_data['end'].isna())
    assert all(raw_data['start'] <= raw_data['end'])

    new_data: DataFrame = DataFrame({
        'gene_id': [],
        'start': [],
        'end': [],
        'intron_end': []
    })

    for gene_id in tqdm(raw_data['gene_id'].unique()):
        assert type(gene_id) is str

        _add_new_data(gene_id=gene_id, raw_data=raw_data, new_data=new_data)

    new_data.to_csv(DNA_EXONS_TABLE_PATH, index=False)


def _add_new_data(gene_id: str, raw_data: DataFrame, new_data: DataFrame):
    indices: Series = raw_data['gene_id'] == gene_id
    gene_data: DataFrame = raw_data.loc[indices]
    gene_data: DataFrame = gene_data.sort_values('start')
    gene_data: list = [row for _, row in gene_data.iterrows()]

    for i, row in enumerate(gene_data):
        start: int = int(row['start'])
        end: int = int(row['end'])

        if i < len(gene_data) - 1:
            intron_end: int = int(gene_data[i+1]['start'])
        else:
            intron_end: float = float('nan')

        new_data.loc[len(new_data)] = [gene_id, start, end, intron_end]


if __name__ == '__main__':
    main()
