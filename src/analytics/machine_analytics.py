from sqlalchemy import text

from src.utils.database import engine


def machine_production_summary():
    query = text("""
        SELECT
            m.machine_id,
            m.machine_name,
            COUNT(pr.production_record_id) AS production_records,
            SUM(pr.actual_quantity) AS total_production,
            AVG(pr.efficiency_percentage) AS average_efficiency
        FROM machines m
        LEFT JOIN production_records pr
            ON m.machine_id = pr.machine_id
        GROUP BY
            m.machine_id,
            m.machine_name
        ORDER BY total_production DESC
    """)

    with engine.connect() as connection:
        return connection.execute(query).fetchall()


def machine_failure_summary():
    query = text("""
        SELECT
            m.machine_id,
            m.machine_name,
            COUNT(mf.failure_id) AS failure_count
        FROM machines m
        LEFT JOIN machine_failures mf
            ON m.machine_id = mf.machine_id
        GROUP BY
            m.machine_id,
            m.machine_name
        ORDER BY failure_count DESC
    """)

    with engine.connect() as connection:
        return connection.execute(query).fetchall()


def machine_downtime_summary():
    query = text("""
        SELECT
            m.machine_id,
            m.machine_name,
            COALESCE(SUM(d.downtime_hours), 0) AS downtime_hours
        FROM machines m
        LEFT JOIN downtime_events d
            ON m.machine_id = d.machine_id
        GROUP BY
            m.machine_id,
            m.machine_name
        ORDER BY downtime_hours DESC
    """)

    with engine.connect() as connection:
        return connection.execute(query).fetchall()


if __name__ == "__main__":

    print("===== MACHINE PRODUCTION SUMMARY =====")

    production = machine_production_summary()

    for row in production[:10]:
        print(
            f"Machine {row.machine_id} | "
            f"{row.machine_name} | "
            f"Production: {row.total_production} | "
            f"Efficiency: {row.average_efficiency:.2f}%"
        )

    print()
    print("===== MACHINE FAILURE SUMMARY =====")

    failures = machine_failure_summary()

    for row in failures[:10]:
        print(
            f"Machine {row.machine_id} | "
            f"{row.machine_name} | "
            f"Failures: {row.failure_count}"
        )

    print()
    print("===== MACHINE DOWNTIME SUMMARY =====")

    downtime = machine_downtime_summary()

    for row in downtime[:10]:
        print(
            f"Machine {row.machine_id} | "
            f"{row.machine_name} | "
            f"Downtime: {row.downtime_hours:.2f} hours"
        )