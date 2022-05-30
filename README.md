# cDNA Web App Back End
## Create database CSV files from raw data
Run the following using `singularity shell` or `singularity exec` after having executing `singularity run`. Make sure to be in the correct directory.
```
python3 api/migrations/data/make_genes_table.py
python3 api/migrations/data/make_transcripts_table.py
python3 api/migrations/data/make_expression_levels_table.py
python3 api/migrations/data/make_transcript_exons_table.py
python3 api/migrations/data/make_dna_exons_table.py
python3 api/migrations/data/make_coverages_table.py
```
## Create database schema and load data from CSV files into it
Run the following after creating the CSV files
```
python3 manage.py migrate api --settings=back_end.settings.local
```
## Run the server in the local development environment
```
bash run-local.sh
```
## Run the server in the staging environment (make sure to provide the SECRET_KEY)
```
SECRET_KEY=<secret_key> bash run-staging.sh
```
## Run the server in production environment (make sure to provide the SECRET_KEY)
```
SECRET_KEY=<secret_key> bash run-production.sh
```
