from pandas import DataFrame, read_csv
from numpy import isnan


def _df_to_db(Model: type, df_path: str) -> list:
    df: DataFrame = read_csv(df_path)
    db_models: list = []

    for _, df_row in df.iterrows():
        df_row: dict = df_row.to_dict()

        for field, value in df_row.items():
            if type(value) is float and isnan(value):
                df_row[field] = None

        model: Model = Model(**df_row)
        db_models.append(model)

    return db_models


def insert_objects(apps, model_class_name: str, df_path: str):
    Model: type = apps.get_model('api', model_class_name)
    db_models: list = _df_to_db(Model=Model, df_path=df_path)
    Model.objects.bulk_create(db_models)


def delete_objects(apps, model_class_name: str):
    Model = apps.get_model('api', model_class_name)
    Model.objects.all().delete()
