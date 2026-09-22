import sqlite3
from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "database"
    / "apex_manufacturing.db"
)

MODEL_DIRECTORY = (
    PROJECT_ROOT
    / "src"
    / "ml"
    / "models"
)

MODEL_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

MODEL_PATH = (
    MODEL_DIRECTORY
    / "machine_failure_model.joblib"
)


def load_data():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    sensors = pd.read_sql_query(
        """
        SELECT *
        FROM sensor_readings
        """,
        connection,
    )

    failures = pd.read_sql_query(
        """
        SELECT *
        FROM machine_failures
        """,
        connection,
    )

    connection.close()

    return sensors, failures


def prepare_dataset(
    sensors,
    failures,
):

    print("Sensor columns:")
    print(list(sensors.columns))

    print()
    print("Failure columns:")
    print(list(failures.columns))
    print()

    # Your database uses recorded_at
    # for sensor timestamps.
    sensor_date_column = "recorded_at"

    # Your database uses failure_date
    # for failure timestamps.
    failure_date_column = "failure_date"

    if sensor_date_column not in sensors.columns:

        raise ValueError(
            f"Missing sensor date column: "
            f"{sensor_date_column}"
        )

    if failure_date_column not in failures.columns:

        raise ValueError(
            f"Missing failure date column: "
            f"{failure_date_column}"
        )

    sensors[sensor_date_column] = pd.to_datetime(
        sensors[sensor_date_column]
    )

    failures[failure_date_column] = pd.to_datetime(
        failures[failure_date_column]
    )

    # Every sensor reading starts as
    # a non-failure example.
    sensors["failure"] = 0

    # Create a set containing:
    #
    # (machine_id, failure_date)
    #
    # so we can identify sensor readings
    # that occurred on a failure date.

    failure_keys = set(
        zip(
            failures["machine_id"],
            failures[
                failure_date_column
            ].dt.date,
        )
    )

    for index, row in sensors.iterrows():

        key = (
            row["machine_id"],
            row[
                sensor_date_column
            ].date(),
        )

        if key in failure_keys:

            sensors.loc[
                index,
                "failure",
            ] = 1

    return sensors


def train_model(dataset):

    # These columns are identifiers or
    # the target and should not be features.

    excluded_columns = {
        "failure",
        "machine_id",
        "sensor_reading_id",
    }

    # Select numerical sensor measurements.

    numeric_columns = dataset.select_dtypes(
        include=["number"]
    ).columns.tolist()

    feature_columns = [
        column
        for column in numeric_columns
        if column not in excluded_columns
    ]

    if not feature_columns:

        raise ValueError(
            "No numeric sensor features were found."
        )

    X = dataset[
        feature_columns
    ].fillna(0)

    y = dataset["failure"]

    print("Features:")
    print(feature_columns)

    print()
    print("Target distribution:")
    print(y.value_counts())

    # Make sure both classes exist.

    if y.nunique() < 2:

        raise ValueError(
            "The dataset contains only one "
            "failure class. The model needs "
            "both failure and non-failure "
            "examples."
        )

    # Split the data.

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )
    )

    # Random Forest works well as a first
    # baseline for this type of structured data.

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    print()
    print(
        "===== MODEL RESULTS ====="
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    print()
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Show which sensor measurements
    # the model considered important.

    print(
        "===== FEATURE IMPORTANCE ====="
    )

    importance = pd.DataFrame(
        {
            "feature": feature_columns,
            "importance": model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False,
    )

    print(
        importance.to_string(
            index=False
        )
    )

    return (
        model,
        feature_columns,
    )


def main():

    print(
        "===== MACHINE FAILURE MODEL ====="
    )

    print()

    sensors, failures = load_data()

    print(
        f"Loaded sensor readings: "
        f"{len(sensors):,}"
    )

    print(
        f"Loaded failures: "
        f"{len(failures):,}"
    )

    print()

    dataset = prepare_dataset(
        sensors,
        failures,
    )

    print(
        f"Prepared training rows: "
        f"{len(dataset):,}"
    )

    print()

    model, feature_columns = (
        train_model(dataset)
    )

    artifact = {
        "model": model,
        "features": feature_columns,
    }

    joblib.dump(
        artifact,
        MODEL_PATH,
    )

    print()

    print(
        f"Model saved to:"
    )

    print(
        MODEL_PATH
    )


if __name__ == "__main__":

    main()