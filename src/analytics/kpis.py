from sqlalchemy import text

from src.utils.database import engine


def total_production():
    query = text("""
        SELECT SUM(actual_quantity)
        FROM production_records
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def average_efficiency():
    query = text("""
        SELECT AVG(efficiency_percentage)
        FROM production_records
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def total_downtime_hours():
    query = text("""
        SELECT SUM(downtime_hours)
        FROM downtime_events
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def total_failures():
    query = text("""
        SELECT COUNT(*)
        FROM machine_failures
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def total_quality_inspections():
    query = text("""
        SELECT COUNT(*)
        FROM quality_inspections
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def defect_count():
    query = text("""
        SELECT COUNT(*)
        FROM quality_inspections
        WHERE defect_found = 1
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


def average_quality_score():
    query = text("""
        SELECT AVG(quality_score)
        FROM quality_inspections
    """)

    with engine.connect() as connection:
        return connection.execute(query).scalar()


if __name__ == "__main__":

    print("===== MANUFACTURING KPIs =====")
    print()

    production = total_production()
    efficiency = average_efficiency()
    downtime = total_downtime_hours()
    failures = total_failures()
    inspections = total_quality_inspections()
    defects = defect_count()
    quality = average_quality_score()

    print(f"Total production: {production:,.0f}")
    print(f"Average efficiency: {efficiency:.2f}%")
    print(f"Total downtime: {downtime:,.2f} hours")
    print(f"Total failures: {failures:,}")
    print(f"Quality inspections: {inspections:,}")
    print(f"Defects found: {defects:,}")
    print(f"Average quality score: {quality:.2f}")