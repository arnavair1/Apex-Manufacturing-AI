import pandas as pd

from src.data_generation.config import GeneratorConfig
from src.data_generation.generator import ManufacturingDataGenerator


def test_generated_data_contains_expected_tables():
    config = GeneratorConfig(
        number_of_factories=2,
        lines_per_factory=2,
        machines_per_line=2,
        number_of_days=3,
    )

    generator = ManufacturingDataGenerator(config)
    datasets = generator.generate_all()

    expected_tables = {
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
    }

    assert set(datasets.keys()) == expected_tables


def test_machine_relationships_are_valid():
    config = GeneratorConfig(
        number_of_factories=2,
        lines_per_factory=2,
        machines_per_line=2,
        number_of_days=3,
    )

    generator = ManufacturingDataGenerator(config)
    datasets = generator.generate_all()

    machines = datasets["machines"]
    lines = datasets["production_lines"]
    factories = datasets["factories"]

    assert machines["line_id"].isin(lines["line_id"]).all()
    assert lines["factory_id"].isin(factories["factory_id"]).all()


def test_generated_objects_are_dataframes():
    config = GeneratorConfig(
        number_of_factories=1,
        lines_per_factory=1,
        machines_per_line=1,
        number_of_days=1,
    )

    generator = ManufacturingDataGenerator(config)
    datasets = generator.generate_all()

    for dataframe in datasets.values():
        assert isinstance(dataframe, pd.DataFrame)