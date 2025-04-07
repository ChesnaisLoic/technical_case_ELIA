import logging
import os
import requests
import pandas as pd
from database import database_initialization, engine

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(message)s", filename="debug.log", encoding="utf-8", level=logging.DEBUG)

OUTPUT_DIRECTORY = "./output"

EXTRACT_OUTPUT_DIRECTORY = f"{OUTPUT_DIRECTORY}/extract"
TRANSFORM_OUTPUT_DIRECTORY = f"{OUTPUT_DIRECTORY}/transform"

exported_config = [
    {
        "url": "https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods126/exports/csv?where=datetime%20%3E%20%272024-08%27%20AND%20datetime%20%3C%20%272024-10%27&limit=-1&lang=fr&timezone=UTC&use_labels=false&epsg=4326",
        "filename": "elia_ods126_202409.csv",
        "tablename": "current_system_imbalance",
    },
    {
        "url": "https://opendata.elia.be/api/explore/v2.1/catalog/datasets/ods134/exports/csv?where=datetime%20%3E%20%272024-08%27%20and%20datetime%20%3C%20%272024-10%27&limit=-1&lang=fr&timezone=UTC&use_labels=false&epsg=4326",
        "filename": "elia_ods134_202409.csv",
        "tablename": "imbalance_prices_per_quarter-hour",
    },
]


def extract(url: str, filename: str) -> None:
    try:
        response = requests.get(url, timeout=600)
    except requests.exceptions.Timeout as exception:
        logging.error(f"Operation timed out : {exception}")
        raise exception

    if response.status_code == 200:
        with open(f"{EXTRACT_OUTPUT_DIRECTORY}/{filename}", "wb") as f:
            f.write(response.content)


def transform(filename: str) -> None:
    extracted_filepath = f"{EXTRACT_OUTPUT_DIRECTORY}/{filename}"
    if not os.path.exists(extracted_filepath):
        logging.error(f"Directory or file not found : {extracted_filepath}")
        return

    dataframe = pd.read_csv(extracted_filepath, delimiter=";")

    # print(dataframe.head())
    # dataframe.info()
    # print(dataframe.describe())
    # print(dataframe.columns)
    # print(f"Nombre de lignes : {len(dataframe)}")
    # print(dataframe["datetime"].head())  # Affiche les premières valeurs
    # print(dataframe["datetime"].dtype)  # Devrait être datetime64[ns]
    # print(dataframe["datetime"].head())  # Affiche les premières valeurs
    # print(dataframe["datetime"].dtype)  # Devrait être datetime64[ns]
    # print(dataframe.isna().sum())

    dataframe["datetime"] = pd.to_datetime(dataframe["datetime"])

    dataframe.to_csv(f"{TRANSFORM_OUTPUT_DIRECTORY}/{filename}", index=False)


def load(filename: str, tablename: str) -> None:
    transformed_filepath = f"{TRANSFORM_OUTPUT_DIRECTORY}/{filename}"
    if not os.path.exists(transformed_filepath):
        logging.error(f"Directory or file not found : {transformed_filepath}")
        return
    dataframe = pd.read_csv(transformed_filepath)

    database_initialization()

    dataframe.to_sql(tablename, engine, index=False, if_exists="append", method="multi", chunksize=2000)


def application():
    logging.info("Starting ETL job")
    for dataset_config in exported_config:
        extract(url=dataset_config["url"], filename=dataset_config["filename"])
        transform(filename=dataset_config["filename"])
        load(filename=dataset_config["filename"], tablename=dataset_config["tablename"])
        logging.info(f"Finished job : proccessing {dataset_config['filename']}")
    logging.info("ETL job completed")


if __name__ == "__main__":
    application()
