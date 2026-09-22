from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIRECTORY = PROJECT_ROOT / "data" / "raw"

DATABASE_DIRECTORY = PROJECT_ROOT / "data" / "database"

DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIRECTORY / "apex_manufacturing.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


def get_engine():
    """Create and return the SQLite database engine."""
    return create_engine(DATABASE_URL)


def load_csv_data() -> dict[str, pd.DataFrame]:
    """Load all generated CSV files into pandas DataFrames."""

    datasets = {}

    for csv_file in DATA_DIRECTORY.glob("*.csv"):
        table_name = csv_file.stem

        datasets[table_name] = pd.read_csv(csv_file)

    return datasets


def load_data_into_database() -> None:
    """Load all CSV datasets into the SQLite database."""

    engine = get_engine()

    datasets = load_csv_data()

    for table_name, dataframe in datasets.items():
        dataframe.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False,
        )

        print(
            f"Loaded {table_name}: "
            f"{len(dataframe):,} rows"
        )

    print()
    print(f"Database created at: {DATABASE_PATH}")


if __name__ == "__main__":
    load_data_into_database()