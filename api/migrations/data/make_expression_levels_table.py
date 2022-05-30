from pandas import read_csv, DataFrame, Index, Series
from numpy import isnan
from tqdm import tqdm

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_bah_transcript_annotation_and_cpm_cDNA.csv'
EXPRESSION_LEVELS_TABLE_PATH: str = 'api/migrations/data/expression_levels.csv'


def main():
    data: DataFrame = read_csv(RAW_TABLE_PATH, usecols=_get_cols_to_include())

    new_data: dict = {
        'transcript_id': [],
        'sample_id': [],
        'expression_level': []
    }

    sample_id_cols: Index = data.columns[1:]
    id_start: str = 'sample_'
    id_end: str = '_n_CPM'

    for sample_id in tqdm(sample_id_cols):
        assert sample_id.startswith(id_start)
        assert sample_id.endswith(id_end)

        rows: zip = zip(data['transcript_id'], data[sample_id])
        sample_id: int = int(sample_id.split(id_start)[-1].split(id_end)[0])

        for transcript_id, expression_level in rows:
            assert type(transcript_id) is str
            assert type(expression_level) == float
            assert not isnan(expression_level)

            new_data['transcript_id'].append(transcript_id)
            new_data['sample_id'].append(sample_id)
            new_data['expression_level'].append(expression_level)

    data: DataFrame = DataFrame(new_data)

    assert data['sample_id'].nunique() == len(sample_id_cols)
    assert data['transcript_id'].nunique() < len(data)
    assert data['sample_id'].nunique() < len(data)

    for sample_id in data['sample_id'].unique():
        indices: Series = data['sample_id'] == sample_id
        sample_transcripts: DataFrame = data.loc[indices]

        assert sample_transcripts['transcript_id'].nunique() == len(sample_transcripts)

    data.to_csv(EXPRESSION_LEVELS_TABLE_PATH, index=False)


def _get_cols_to_include() -> list:
    cols_to_exclude: set = {
        'chr', 'type', 'start', 'end', 'strand', 'subtype', 'is_novel_transcript', 'is_novel_gene', 'transcript_name',
        'gene_id', 'gene_name', 'start_codon', 'stop_codon'
    }

    columns: DataFrame = read_csv(RAW_TABLE_PATH, nrows=0)
    columns: Index = columns.columns
    cols_to_include: list = []

    for column in columns:
        if column not in cols_to_exclude:
            cols_to_include.append(column)

    return cols_to_include


if __name__ == '__main__':
    main()
