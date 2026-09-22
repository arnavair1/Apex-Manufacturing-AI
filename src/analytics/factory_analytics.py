from sqlalchemy import text

from src.utils.database import engine


def factory_performance():
    query = text("""
        SELECT
            f.factory_id,
            f.factory_name,
            COUNT(DISTINCT m.machine_id) AS machine_count,
            SUM(pr.actual_quantity) AS total_production,
            AVG(pr.efficiency_percentage) AS average_efficiency
        FROM factories f
        LEFT JOIN production_lines pl
            ON f.factory_id = pl.factory_id
        LEFT JOIN machines m
            ON pl.line_id = m.line_id
        LEFT JOIN production_records pr
            ON m.machine_id = pr.machine_id
        GROUP BY
            f.factory_id,
            f.factory_name
        ORDER BY total_production DESC
    """)

    with engine.connect() as connection:
        return connection.execute(query).fetchall()


def factory_failures():
    query = text("""
        SELECT
            f.factory_id,
            f.factory_name,
            COUNT(mf.failure_id) AS failure_count
        FROM factories f
        LEFT JOIN production_lines pl
            ON f.factory_id = pl.factory_id
        LEFT JOIN machines m
            ON pl.line_id = m.line_id
        LEFT JOIN machine_failures mf
            ON m.machine_id = mf.machine_id
        GROUP BY
            f.factory_id,
            f.factory_name
        ORDER BY failure_count DESC
    """)

    with engine.connect() as connection:
        return connection.execute(query).fetchall()


if __name__ == "__main__":

    print("===== FACTORY PERFORMANCE =====")

    performance = factory_performance()

    for row in performance:
        print(
            f"Factory {row.factory_id} | "
            f"{row.factory_name} | "
            f"Machines: {row.machine_count} | "
            f"Production: {row.total_production} | "
            f"Efficiency: {row.average_efficiency:.2f}%"
        )

    print()
    print("===== FACTORY FAILURES =====")

    failures = factory_failures()

    for row in failures:
        print(
            f"Factory {row.factory_id} | "
            f"{row.factory_name} | "
            f"Failures: {row.failure_count}"
        )