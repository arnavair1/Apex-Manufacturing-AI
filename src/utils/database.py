from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"
DATABASE_DIRECTORY = PROJECT_ROOT / "database"

DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIRECTORY / "apex_manufacturing.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL)


DATASETS = [
    "factories",
    "production_lines",
    "machines",
    "products",
    "suppliers",
    "employees",
    "production_records",
    "sensor_readings",
    "machine_failures",
    "downtime_events",
    "maintenance_records",
    "quality_inspections",
]


def load_csv_data() -> None:
    """Load every generated CSV file into the SQLite database."""

    for dataset_name in DATASETS:
        csv_path = DATA_DIRECTORY / f"{dataset_name}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing dataset: {csv_path}"
            )

        dataframe = pd.read_csv(csv_path)

        dataframe.to_sql(
            dataset_name,
            engine,
            if_exists="replace",
            index=False,
        )

        print(
            f"Loaded {dataset_name}: "
            f"{len(dataframe):,} rows"
        )


if __name__ == "__main__":
    load_csv_data()

    print()
    print(f"Database created: {DATABASE_PATH}")