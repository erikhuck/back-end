from django.db import models


def _get_max_length_of_choices(choices: tuple) -> int:
    return max([max(len(choice[0]), len(choice[1])) for choice in choices])


class Gene(models.Model):
    gene_id = models.CharField(max_length=50, primary_key=True, null=False, unique=True)
    gene_name = models.CharField(max_length=50, null=True, unique=False)


class Transcript(models.Model):
    transcript_id = models.CharField(max_length=50, primary_key=True, null=False, unique=True)
    transcript_name = models.CharField(max_length=50, null=True, unique=False)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=False, unique=False)


class ExpressionLevel(models.Model):
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=False, unique=False)
    sample_id = models.IntegerField(null=False, unique=False)
    expression_level = models.FloatField(null=False, unique=False)


class TranscriptExon(models.Model):
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=False, unique=False)
    start = models.IntegerField(null=False, unique=False)
    end = models.IntegerField(null=False, unique=False)

    exon_region_type_choices: tuple = (
        ('TRANSLATED', 'TRANSLATED'),
        ('UNTRANSLATED_OR_UNKNOWN', 'UNTRANSLATED_OR_UNKNOWN'),
        ('NOVEL_TRANSCRIPT', 'NOVEL_TRANSCRIPT'),
        ('NOVEL_EXON', 'NOVEL_EXON')
    )

    max_length: int = _get_max_length_of_choices(choices=exon_region_type_choices)

    exon_region_type = models.CharField(
        max_length=max_length, choices=exon_region_type_choices, null=False, unique=False
    )

    intron_region_type_choices: tuple = (
        ('KNOWN_JUNCTION', 'KNOWN_JUNCTION'),
        ('NOVEL_JUNCTION', 'NOVEL_JUNCTION'),
        ('NO_JUNCTION', 'NO_JUNCTION')
    )

    max_length: int = _get_max_length_of_choices(choices=intron_region_type_choices)

    intron_region_type = models.CharField(
        max_length=max_length, choices=intron_region_type_choices, null=False, unique=False
    )

    intron_end: int = models.IntegerField(null=True, unique=False)


class DnaExon(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=False, unique=False)
    start = models.IntegerField(null=False, unique=False)
    end = models.IntegerField(null=False, unique=False)
    intron_end: int = models.IntegerField(null=True, unique=False)


class Coverage(models.Model):
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=False, unique=False)
    down_sample_percent = models.FloatField(null=False, unique=False)
    illumina_average_coverage = models.FloatField(null=False, unique=False)
    nanopore_average_coverage = models.FloatField(null=False, unique=False)
