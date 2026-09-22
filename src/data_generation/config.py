from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratorConfig:
    """
    Controls the size and behavior of the synthetic manufacturing dataset.
    """

    seed: int = 42

    number_of_factories: int = 5
    lines_per_factory: int = 3
    machines_per_line: int = 4

    number_of_products: int = 10
    number_of_suppliers: int = 8
    number_of_employees: int = 100

    number_of_days: int = 30
    records_per_machine_per_day: int = 2
    sensor_readings_per_machine_per_day: int = 6

    failure_probability: float = 0.04
    maintenance_probability: float = 0.12
    quality_inspection_probability: float = 0.35