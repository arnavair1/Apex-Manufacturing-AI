from pathlib import Path

import joblib
from sqlalchemy import text

from src.utils.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "src"
    / "ml"
    / "models"
    / "machine_failure_model.joblib"
)


def get_overall_kpis():
    """
    Return overall manufacturing KPIs.
    """

    with engine.connect() as connection:

        production = connection.execute(
            text(
                """
                SELECT
                    SUM(actual_quantity) AS total_production,
                    AVG(efficiency_percentage) AS average_efficiency
                FROM production_records
                """
            )
        ).mappings().one()

        failures = connection.execute(
            text(
                """
                SELECT COUNT(*) AS failure_count
                FROM machine_failures
                """
            )
        ).mappings().one()

        quality = connection.execute(
            text(
                """
                SELECT
                    COUNT(*) AS inspection_count,
                    SUM(
                        CASE
                            WHEN defect_found = 1 THEN 1
                            ELSE 0
                        END
                    ) AS defect_count,
                    AVG(quality_score) AS average_quality_score
                FROM quality_inspections
                """
            )
        ).mappings().one()

    return {
        "total_production": production["total_production"],
        "average_efficiency": production["average_efficiency"],
        "failure_count": failures["failure_count"],
        "inspection_count": quality["inspection_count"],
        "defect_count": quality["defect_count"],
        "average_quality_score": quality[
            "average_quality_score"
        ],
    }


def get_machine_summary(machine_id=None):
    """
    Return production, failure, downtime, and basic machine
    information.

    Separate aggregate queries are used so that joins do not
    multiply rows and inflate totals.
    """

    with engine.connect() as connection:

        machine_query = """
            SELECT
                machine_id,
                line_id,
                machine_name,
                machine_type,
                installation_date,
                age_years,
                criticality
            FROM machines
        """

        parameters = {}

        if machine_id is not None:
            machine_query += """
                WHERE machine_id = :machine_id
            """
            parameters["machine_id"] = machine_id

        machine_rows = connection.execute(
            text(machine_query),
            parameters,
        ).mappings().fetchall()

        results = []

        for machine in machine_rows:

            current_machine_id = machine["machine_id"]

            production = connection.execute(
                text(
                    """
                    SELECT
                        COALESCE(
                            SUM(actual_quantity),
                            0
                        ) AS total_production,
                        COALESCE(
                            AVG(efficiency_percentage),
                            0
                        ) AS average_efficiency,
                        COUNT(*) AS production_records
                    FROM production_records
                    WHERE machine_id = :machine_id
                    """
                ),
                {
                    "machine_id": current_machine_id
                },
            ).mappings().one()

            failures = connection.execute(
                text(
                    """
                    SELECT
                        COUNT(*) AS failure_count,
                        MAX(failure_date)
                            AS most_recent_failure
                    FROM machine_failures
                    WHERE machine_id = :machine_id
                    """
                ),
                {
                    "machine_id": current_machine_id
                },
            ).mappings().one()

            downtime = connection.execute(
                text(
                    """
                    SELECT
                        COUNT(*) AS downtime_events,
                        COALESCE(
                            SUM(downtime_hours),
                            0
                        ) AS total_downtime_hours,
                        COALESCE(
                            MAX(downtime_hours),
                            0
                        ) AS longest_downtime_event
                    FROM downtime_events
                    WHERE machine_id = :machine_id
                    """
                ),
                {
                    "machine_id": current_machine_id
                },
            ).mappings().one()

            result = dict(machine)

            result.update(
                {
                    "total_production":
                        production["total_production"],
                    "average_efficiency":
                        production["average_efficiency"],
                    "production_records":
                        production["production_records"],
                    "failure_count":
                        failures["failure_count"],
                    "most_recent_failure":
                        failures["most_recent_failure"],
                    "downtime_events":
                        downtime["downtime_events"],
                    "total_downtime_hours":
                        downtime[
                            "total_downtime_hours"
                        ],
                    "longest_downtime_event":
                        downtime[
                            "longest_downtime_event"
                        ],
                }
            )

            results.append(result)

    return results


def get_factory_summary(factory_id=None):
    """
    Return factory-level production and machine information.
    """

    with engine.connect() as connection:

        query = """
            SELECT
                f.factory_id,
                f.factory_name,
                COUNT(DISTINCT pl.line_id)
                    AS line_count,
                COUNT(DISTINCT m.machine_id)
                    AS machine_count,
                COALESCE(
                    SUM(pr.actual_quantity),
                    0
                ) AS total_production,
                COALESCE(
                    AVG(pr.efficiency_percentage),
                    0
                ) AS average_efficiency
            FROM factories f

            LEFT JOIN production_lines pl
                ON pl.factory_id = f.factory_id

            LEFT JOIN machines m
                ON m.line_id = pl.line_id

            LEFT JOIN production_records pr
                ON pr.machine_id = m.machine_id
        """

        parameters = {}

        if factory_id is not None:

            query += """
                WHERE f.factory_id = :factory_id
            """

            parameters["factory_id"] = factory_id

        query += """
            GROUP BY
                f.factory_id,
                f.factory_name

            ORDER BY
                average_efficiency ASC
        """

        rows = connection.execute(
            text(query),
            parameters,
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def get_machine_sensor_readings(
    machine_id=None,
    limit=20,
):
    """
    Return recent sensor readings.
    """

    query = """
        SELECT
            sensor_reading_id,
            machine_id,
            recorded_at,
            temperature_celsius,
            vibration_mm_s,
            pressure_psi
        FROM sensor_readings
    """

    parameters = {}

    if machine_id is not None:

        query += """
            WHERE machine_id = :machine_id
        """

        parameters["machine_id"] = machine_id

    query += """
        ORDER BY recorded_at DESC
        LIMIT :limit
    """

    parameters["limit"] = limit

    with engine.connect() as connection:

        rows = connection.execute(
            text(query),
            parameters,
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def get_machine_failures(machine_id=None):
    """
    Return machine failure history.
    """

    query = """
        SELECT
            failure_id,
            machine_id,
            failure_date,
            failure_type,
            severity,
            failure_description
        FROM machine_failures
    """

    parameters = {}

    if machine_id is not None:

        query += """
            WHERE machine_id = :machine_id
        """

        parameters["machine_id"] = machine_id

    query += """
        ORDER BY failure_date DESC
    """

    with engine.connect() as connection:

        rows = connection.execute(
            text(query),
            parameters,
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def get_machine_downtime(machine_id=None):
    """
    Return downtime history.
    """

    query = """
        SELECT
            downtime_event_id,
            machine_id,
            failure_id,
            downtime_date,
            downtime_hours,
            reason
        FROM downtime_events
    """

    parameters = {}

    if machine_id is not None:

        query += """
            WHERE machine_id = :machine_id
        """

        parameters["machine_id"] = machine_id

    query += """
        ORDER BY downtime_date DESC
    """

    with engine.connect() as connection:

        rows = connection.execute(
            text(query),
            parameters,
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def get_quality_summary(machine_id=None):
    """
    Return quality inspection information.
    """

    query = """
        SELECT
            machine_id,
            COUNT(*) AS inspection_count,
            SUM(
                CASE
                    WHEN defect_found = 1 THEN 1
                    ELSE 0
                END
            ) AS defect_count,
            AVG(quality_score) AS average_quality_score
        FROM quality_inspections
    """

    parameters = {}

    if machine_id is not None:

        query += """
            WHERE machine_id = :machine_id
        """

        parameters["machine_id"] = machine_id

    query += """
        GROUP BY machine_id
    """

    with engine.connect() as connection:

        rows = connection.execute(
            text(query),
            parameters,
        ).mappings().fetchall()

    return [dict(row) for row in rows]


def search_manufacturing_knowledge(
    query,
    top_k=3,
):
    """
    Search the manufacturing RAG knowledge base.
    """

    from src.rag.retrieve import retrieve_documents

    return retrieve_documents(
        query,
        top_k=top_k,
    )


def predict_machine_failure(
    temperature_celsius,
    vibration_mm_s,
    pressure_psi,
):
    """
    Predict machine failure probability using the trained
    machine-learning model.

    The saved joblib file contains a dictionary with the
    trained model and metadata. This function extracts the
    actual model before calling predict() and predict_proba().
    """

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            "Failure prediction model not found. "
            "Run src/ml/train_failure_model.py first."
        )

    saved_object = joblib.load(
        MODEL_PATH
    )

    # The training script saved a dictionary.
    # Extract the actual sklearn model from it.
    if isinstance(saved_object, dict):

        model = saved_object.get(
            "model"
        )

        if model is None:

            raise ValueError(
                "The saved failure model is a dictionary, "
                "but it does not contain a 'model' entry."
            )

    else:

        # Backward compatibility if the file contains
        # the model directly.
        model = saved_object

    prediction_input = [[
        temperature_celsius,
        vibration_mm_s,
        pressure_psi,
    ]]

    prediction = model.predict(
        prediction_input
    )[0]

    probabilities = model.predict_proba(
        prediction_input
    )[0]

    failure_probability = float(
        probabilities[1]
    )

    return {
        "failure_prediction":
            int(prediction),
        "failure_probability":
            failure_probability,
        "model_features": [
            "temperature_celsius",
            "vibration_mm_s",
            "pressure_psi",
        ],
    }


def investigate_machine(machine_id):
    """
    Gather a compact evidence package for one machine.

    This is intended for deeper investigation after a machine
    has been identified for further review.
    """

    summary = get_machine_summary(
        machine_id
    )

    sensor_readings = get_machine_sensor_readings(
        machine_id,
        limit=10,
    )

    failures = get_machine_failures(
        machine_id
    )

    downtime = get_machine_downtime(
        machine_id
    )

    quality = get_quality_summary(
        machine_id
    )

    return {
        "machine_summary": summary,
        "recent_sensor_readings":
            sensor_readings,
        "failures":
            failures,
        "downtime":
            downtime,
        "quality":
            quality,
    }


def get_machine_attention_signals():
    """
    Return objective machine-level evidence that can help
    identify machines deserving further investigation.

    This function does NOT decide that a machine is unsafe
    or guaranteed to fail.

    It gathers:

    - production
    - efficiency
    - failure count
    - downtime
    - recent sensor readings
    - historical sensor averages
    - recent sensor deviation from historical averages
    - machine criticality
    """

    with engine.connect() as connection:

        rows = connection.execute(
            text(
                """
                WITH production_summary AS (

                    SELECT
                        machine_id,

                        SUM(actual_quantity)
                            AS total_production,

                        AVG(efficiency_percentage)
                            AS average_efficiency

                    FROM production_records

                    GROUP BY machine_id
                ),

                failure_summary AS (

                    SELECT
                        machine_id,

                        COUNT(*) AS failure_count,

                        MAX(failure_date)
                            AS most_recent_failure

                    FROM machine_failures

                    GROUP BY machine_id
                ),

                downtime_summary AS (

                    SELECT
                        machine_id,

                        COUNT(*) AS downtime_events,

                        SUM(downtime_hours)
                            AS total_downtime_hours,

                        MAX(downtime_hours)
                            AS longest_downtime_event

                    FROM downtime_events

                    GROUP BY machine_id
                ),

                sensor_history AS (

                    SELECT
                        machine_id,

                        AVG(temperature_celsius)
                            AS average_temperature,

                        AVG(vibration_mm_s)
                            AS average_vibration,

                        AVG(pressure_psi)
                            AS average_pressure

                    FROM sensor_readings

                    GROUP BY machine_id
                ),

                latest_sensor AS (

                    SELECT
                        sr.machine_id,

                        sr.recorded_at,

                        sr.temperature_celsius,

                        sr.vibration_mm_s,

                        sr.pressure_psi

                    FROM sensor_readings sr

                    INNER JOIN (

                        SELECT
                            machine_id,

                            MAX(recorded_at)
                                AS latest_recorded_at

                        FROM sensor_readings

                        GROUP BY machine_id

                    ) latest

                    ON sr.machine_id =
                       latest.machine_id

                    AND sr.recorded_at =
                        latest.latest_recorded_at
                )

                SELECT

                    m.machine_id,

                    m.machine_name,

                    m.machine_type,

                    m.line_id,

                    m.installation_date,

                    m.age_years,

                    m.criticality,

                    COALESCE(
                        ps.total_production,
                        0
                    ) AS total_production,

                    COALESCE(
                        ps.average_efficiency,
                        0
                    ) AS average_efficiency,

                    COALESCE(
                        fs.failure_count,
                        0
                    ) AS failure_count,

                    fs.most_recent_failure,

                    COALESCE(
                        ds.downtime_events,
                        0
                    ) AS downtime_events,

                    COALESCE(
                        ds.total_downtime_hours,
                        0
                    ) AS total_downtime_hours,

                    COALESCE(
                        ds.longest_downtime_event,
                        0
                    ) AS longest_downtime_event,

                    ls.recorded_at
                        AS latest_sensor_time,

                    ls.temperature_celsius
                        AS latest_temperature,

                    ls.vibration_mm_s
                        AS latest_vibration,

                    ls.pressure_psi
                        AS latest_pressure,

                    sh.average_temperature,

                    sh.average_vibration,

                    sh.average_pressure,

                    (
                        ls.temperature_celsius
                        - sh.average_temperature
                    ) AS temperature_deviation,

                    (
                        ls.vibration_mm_s
                        - sh.average_vibration
                    ) AS vibration_deviation,

                    (
                        ls.pressure_psi
                        - sh.average_pressure
                    ) AS pressure_deviation

                FROM machines m

                LEFT JOIN production_summary ps
                    ON ps.machine_id =
                       m.machine_id

                LEFT JOIN failure_summary fs
                    ON fs.machine_id =
                       m.machine_id

                LEFT JOIN downtime_summary ds
                    ON ds.machine_id =
                       m.machine_id

                LEFT JOIN sensor_history sh
                    ON sh.machine_id =
                       m.machine_id

                LEFT JOIN latest_sensor ls
                    ON ls.machine_id =
                       m.machine_id

                ORDER BY

                    COALESCE(
                        ds.total_downtime_hours,
                        0
                    ) DESC,

                    COALESCE(
                        fs.failure_count,
                        0
                    ) DESC,

                    COALESCE(
                        ps.average_efficiency,
                        0
                    ) ASC
                """
            )
        ).mappings().fetchall()

    return [
        dict(row)
        for row in rows
    ]


AVAILABLE_TOOLS = {

    "get_overall_kpis":
        get_overall_kpis,

    "get_machine_summary":
        get_machine_summary,

    "get_factory_summary":
        get_factory_summary,

    "get_machine_sensor_readings":
        get_machine_sensor_readings,

    "get_machine_failures":
        get_machine_failures,

    "get_machine_downtime":
        get_machine_downtime,

    "get_quality_summary":
        get_quality_summary,

    "search_manufacturing_knowledge":
        search_manufacturing_knowledge,

    "predict_machine_failure":
        predict_machine_failure,

    "investigate_machine":
        investigate_machine,

    "get_machine_attention_signals":
        get_machine_attention_signals,
}