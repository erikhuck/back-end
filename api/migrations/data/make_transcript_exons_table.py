from pandas import read_csv, DataFrame, Series
from numpy import isnan
from tqdm import tqdm

RAW_TABLE_PATH: str = 'api/migrations/data/2022-05-13_bah_exon_annotation_cDNA.csv'
TRANSCRIPT_EXONS_TABLE_PATH: str = 'api/migrations/data/transcript_exons.csv'
START_CODONS_DOWNSTREAM_FROM_TRANSCRIPT: set = set()
START_CODONS_UPSTREAM_FROM_TRANSCRIPT: set = set()
STOP_CODONS_UPSTREAM_FROM_TRANSCRIPT: set = set()
STOP_CODONS_DOWNSTREAM_FROM_TRANSCRIPT: set = set()
STARTS_GREATER_THAN_OR_EQUAL_TO_END: set = set()


def main():
    cols_to_include: list = [
        'start', 'end', 'transcript_id', 'start_codon', 'stop_codon', 'is_novel_transcript', 'is_novel_exon',
        'is_novel_junction'
    ]

    new_data: DataFrame = DataFrame({
        'transcript_id': [],
        'start': [],
        'end': [],
        'exon_region_type': [],
        'intron_region_type': [],
        'intron_end': []
    })

    raw_data: DataFrame = read_csv(RAW_TABLE_PATH, usecols=cols_to_include)

    assert not any(raw_data['transcript_id'].isna())
    assert not any(raw_data['start'].isna())
    assert not any(raw_data['end'].isna())
    assert any(raw_data['start_codon'].isna())
    assert any(raw_data['stop_codon'].isna())
    assert set(raw_data['is_novel_transcript'].unique()) == {True, False}
    assert set(raw_data['is_novel_exon'].unique()) == {True, False}
    assert set(raw_data['is_novel_junction'].unique()) == {True, False}
    assert all(raw_data.loc[raw_data['is_novel_transcript']]['start_codon'].isna())
    assert all(raw_data.loc[raw_data['is_novel_transcript']]['stop_codon'].isna())
    assert any(raw_data.loc[~raw_data['is_novel_transcript']]['start_codon'].isna())
    assert any(raw_data.loc[~raw_data['is_novel_transcript']]['stop_codon'].isna())
    assert not all(raw_data.loc[~raw_data['is_novel_transcript']]['start_codon'].isna())
    assert not all(raw_data.loc[~raw_data['is_novel_transcript']]['stop_codon'].isna())
    assert any(raw_data.loc[raw_data['is_novel_transcript']]['is_novel_exon'])
    assert any(raw_data.loc[raw_data['is_novel_transcript']]['is_novel_junction'])

    for transcript_id in tqdm(raw_data['transcript_id'].unique()):
        assert type(transcript_id) is str

        indices: Series = raw_data['transcript_id'] == transcript_id
        transcript_data: DataFrame = raw_data.loc[indices]
        transcript_data: DataFrame = transcript_data.sort_values('start')

        assert transcript_data['start'].nunique() == len(transcript_data)
        assert transcript_data['end'].nunique() == len(transcript_data)

        _add_transcript_data(transcript_data=transcript_data, new_data=new_data)

        assert all(new_data.loc[new_data['intron_region_type'] == 'NO_JUNCTION']['intron_end'].isna())
        assert not any(new_data.loc[new_data['intron_region_type'] != 'NO_JUNCTION']['intron_end'].isna())

    print('START_CODONS_DOWNSTREAM_FROM_TRANSCRIPT:', *START_CODONS_DOWNSTREAM_FROM_TRANSCRIPT)
    print('START_CODONS_UPSTREAM_FROM_TRANSCRIPT:', *START_CODONS_UPSTREAM_FROM_TRANSCRIPT)
    print('STOP_CODONS_UPSTREAM_FROM_TRANSCRIPT:', *STOP_CODONS_UPSTREAM_FROM_TRANSCRIPT)
    print('STOP_CODONS_DOWNSTREAM_FROM_TRANSCRIPT:', *STOP_CODONS_DOWNSTREAM_FROM_TRANSCRIPT)
    print('STARTS_GREATER_THAN_OR_EQUAL_TO_END:', *STARTS_GREATER_THAN_OR_EQUAL_TO_END)

    new_data.to_csv(TRANSCRIPT_EXONS_TABLE_PATH, index=False)


def _add_transcript_data(transcript_data: DataFrame, new_data: DataFrame):
    is_novel_transcript: bool = transcript_data['is_novel_transcript'].unique().item()

    if is_novel_transcript:
        _add_novel_transcript_data(novel_transcript_data=transcript_data, new_data=new_data)
    else:
        assert transcript_data['is_novel_exon'].unique().item() is False
        assert transcript_data['is_novel_junction'].unique().item() is False

        _add_known_transcript_data(known_transcript_data=transcript_data, new_data=new_data)


def _add_novel_transcript_data(novel_transcript_data: DataFrame, new_data: DataFrame):
    def get_new_data_row(
        transcript_id: str, start: int, end: int, next_raw_data_row: Series, raw_data_row: Series
    ) -> list:
        if raw_data_row['is_novel_exon']:
            exon_region_type: str = 'NOVEL_EXON'
        else:
            exon_region_type: str = 'NOVEL_TRANSCRIPT'

        if raw_data_row['is_novel_junction']:
            intron_region_type: str = 'NOVEL_JUNCTION'
        elif next_raw_data_row is None:
            intron_region_type: str = 'NO_JUNCTION'
        else:
            intron_region_type: str = 'KNOWN_JUNCTION'

        if intron_region_type == 'NO_JUNCTION':
            intron_end: float = float('nan')
        else:
            intron_end: int = int(next_raw_data_row['start'])

        return [transcript_id, start, end, exon_region_type, intron_region_type, intron_end]

    _add_new_data_rows(get_new_data_row=get_new_data_row, transcript_data=novel_transcript_data, new_data=new_data)


def _add_known_transcript_data(known_transcript_data: DataFrame, new_data: DataFrame):
    start_codon = known_transcript_data['start_codon'].unique().item()
    stop_codon = known_transcript_data['stop_codon'].unique().item()

    if isnan(start_codon):
        assert isnan(stop_codon)

        _add_untranslated_or_unknown_transcript_data(
            untranslated_or_unknown_transcript_data=known_transcript_data, new_data=new_data
        )
    else:
        start_codon: int = int(start_codon)
        stop_codon: int = int(stop_codon)

        assert start_codon < stop_codon

        _add_translated_transcript_data(
            start_codon=start_codon, stop_codon=stop_codon, translated_transcript_data=known_transcript_data,
            new_data=new_data
        )


def _add_untranslated_or_unknown_transcript_data(
    untranslated_or_unknown_transcript_data: DataFrame, new_data: DataFrame
):
    """All the exons of this known transcript are either untranslated or it is not known if they are translated"""

    def get_new_data_row(
        transcript_id: str, start: int, end: int, next_raw_data_row: Series, **_
    ) -> list:
        intron_region_type, intron_end = _get_intron_info(next_raw_data_row=next_raw_data_row)

        return [
            transcript_id, start, end, 'UNTRANSLATED_OR_UNKNOWN', intron_region_type, intron_end
        ]

    _add_new_data_rows(
        get_new_data_row=get_new_data_row, transcript_data=untranslated_or_unknown_transcript_data, new_data=new_data
    )


def _get_intron_info(next_raw_data_row: Series) -> tuple:
    if next_raw_data_row is None:
        intron_region_type: str = 'NO_JUNCTION'
        intron_end: float = float('nan')
    else:
        intron_region_type: str = 'KNOWN_JUNCTION'
        intron_end: int = int(next_raw_data_row['start'])

    return intron_region_type, intron_end


def _add_new_data_rows(get_new_data_row: callable, transcript_data: DataFrame, new_data: DataFrame):
    transcript_start: int = int(min(transcript_data['start']))
    transcript_end: int = int(max(transcript_data['end']))

    assert sum(transcript_data['end'] == transcript_end) == 1 and sum(transcript_data['start'] == transcript_start) == 1

    transcript_id: str = transcript_data['transcript_id'].unique().item()
    raw_data_rows: list = [row for _, row in transcript_data.iterrows()]

    for i, raw_data_row in enumerate(raw_data_rows):
        start: int = int(raw_data_row['start'])
        end: int = int(raw_data_row['end'])

        if start >= end:
            STARTS_GREATER_THAN_OR_EQUAL_TO_END.add(transcript_id)

        assert transcript_start <= start <= transcript_end
        assert transcript_start <= end <= transcript_end

        if end == transcript_end:
            next_raw_data_row: None = None
        else:
            next_raw_data_row: Series = raw_data_rows[i+1]

        new_data_row = get_new_data_row(
            transcript_id=transcript_id, start=start, end=end, next_raw_data_row=next_raw_data_row,
            raw_data_row=raw_data_row
        )

        if type(new_data_row) is tuple:
            # Two rows for the new data were created from the single raw data row
            new_data_row1, new_data_row2 = new_data_row
            new_data.loc[len(new_data)] = new_data_row1
            new_data.loc[len(new_data)] = new_data_row2
        else:
            assert type(new_data_row) is list

            new_data.loc[len(new_data)] = new_data_row


def _add_translated_transcript_data(
    start_codon: int, stop_codon: int, translated_transcript_data: DataFrame, new_data: DataFrame
):
    if start_codon < int(min(translated_transcript_data['start'])):
        START_CODONS_UPSTREAM_FROM_TRANSCRIPT.add(translated_transcript_data['transcript_id'].unique().item())
    elif stop_codon < int(min(translated_transcript_data['start'])):
        STOP_CODONS_UPSTREAM_FROM_TRANSCRIPT.add(translated_transcript_data['transcript_id'].unique().item())

    def get_new_data_row(
        transcript_id: str, start: int, end: int, next_raw_data_row: Series, **_
    ):
        intron_region_type, intron_end = _get_intron_info(next_raw_data_row=next_raw_data_row)

        if end <= start_codon:
            # If an exon's end locus is less than the start codon, it is entirely untranslated
            if isnan(intron_end):
                START_CODONS_DOWNSTREAM_FROM_TRANSCRIPT.add(transcript_id)

            return [
                transcript_id, start, end, 'UNTRANSLATED_OR_UNKNOWN', intron_region_type, intron_end
            ]
        elif start <= start_codon <= end:
            # If the start codon is inside of an exon, the portion upstream from the start codon is untranslated
            # The portion downstream from the start codon is translated and there's an intron afterwards
            return (
                [transcript_id, start, start_codon, 'UNTRANSLATED_OR_UNKNOWN', 'NO_JUNCTION', float('nan')],
                [transcript_id, start_codon, end, 'TRANSLATED', intron_region_type, intron_end]
            )
        elif start_codon <= start and end <= stop_codon:
            # If an exon's start locus is greater than the start codon
            # and its end locus is less than the stop codon, it is entirely translated and there's an intron afterwards
            if isnan(intron_end):
                STOP_CODONS_DOWNSTREAM_FROM_TRANSCRIPT.add(transcript_id)

            return [transcript_id, start, end, 'TRANSLATED', intron_region_type, intron_end]
        elif start <= stop_codon <= end:
            # If the stop codon is inside of an exon, the portion upstream from the stop codon is translated
            # while the portion downstream is untranslated
            return (
                [transcript_id, start, stop_codon, 'TRANSLATED', 'NO_JUNCTION', float('nan')],
                [transcript_id, stop_codon, end, 'UNTRANSLATED_OR_UNKNOWN', intron_region_type, intron_end]
            )
        elif start >= stop_codon:
            # If an exon's start locus is greater than the stop codon, it is entirely untranslated
            return [transcript_id, start, end, 'UNTRANSLATED_OR_UNKNOWN', intron_region_type, intron_end]
        else:
            raise Exception(f'Transcript of ID {transcript_id} does not fit any criteria')

    _add_new_data_rows(
        get_new_data_row=get_new_data_row, transcript_data=translated_transcript_data, new_data=new_data
    )


if __name__ == '__main__':
    main()
