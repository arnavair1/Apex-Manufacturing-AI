from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_generation.config import GeneratorConfig


class ManufacturingDataGenerator:
    """
    Generates connected synthetic manufacturing data.

    The generated data is fictional and intended for development,
    analytics, machine learning, and agent testing.
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

        self.factories: pd.DataFrame | None = None
        self.production_lines: pd.DataFrame | None = None
        self.machines: pd.DataFrame | None = None
        self.products: pd.DataFrame | None = None
        self.suppliers: pd.DataFrame | None = None
        self.employees: pd.DataFrame | None = None

        self.production_records: pd.DataFrame | None = None
        self.sensor_readings: pd.DataFrame | None = None
        self.machine_failures: pd.DataFrame | None = None
        self.downtime_events: pd.DataFrame | None = None
        self.maintenance_records: pd.DataFrame | None = None
        self.quality_inspections: pd.DataFrame | None = None

    def generate_all(self) -> dict[str, pd.DataFrame]:
        """
        Generate all connected manufacturing datasets.
        """

        self._generate_master_data()
        self._generate_operational_data()

        return {
            "factories": self.factories,
            "production_lines": self.production_lines,
            "machines": self.machines,
            "products": self.products,
            "suppliers": self.suppliers,
            "employees": self.employees,
            "production_records": self.production_records,
            "sensor_readings": self.sensor_readings,
            "machine_failures": self.machine_failures,
            "downtime_events": self.downtime_events,
            "maintenance_records": self.maintenance_records,
            "quality_inspections": self.quality_inspections,
        }

    def _generate_master_data(self) -> None:
        """Generate factories, lines, machines, products, suppliers, and employees."""

        factory_rows = []

        for factory_number in range(1, self.config.number_of_factories + 1):
            factory_rows.append(
                {
                    "factory_id": f"FAC-{factory_number:03d}",
                    "factory_name": f"Apex Factory {factory_number}",
                    "location": f"Industrial Zone {factory_number}",
                    "factory_type": "Automotive Components",
                }
            )

        self.factories = pd.DataFrame(factory_rows)

        line_rows = []
        machine_rows = []

        for factory_number in range(1, self.config.number_of_factories + 1):
            for line_number in range(1, self.config.lines_per_factory + 1):
                line_id = f"LINE-{factory_number:03d}-{line_number:02d}"
                factory_id = f"FAC-{factory_number:03d}"

                line_rows.append(
                    {
                        "line_id": line_id,
                        "factory_id": factory_id,
                        "line_name": f"Production Line {factory_number}-{line_number}",
                        "line_type": "Assembly",
                    }
                )

                for machine_number in range(
                    1, self.config.machines_per_line + 1
                ):
                    machine_id = (
                        f"MCH-{factory_number:03d}-"
                        f"{line_number:02d}-{machine_number:02d}"
                    )

                    machine_rows.append(
                        {
                            "machine_id": machine_id,
                            "line_id": line_id,
                            "machine_name": f"Machine {machine_id}",
                            "machine_type": self.rng.choice(
                                ["Press", "CNC", "Robot", "Conveyor"]
                            ),
                            "installation_date": (
                                datetime(2019, 1, 1)
                                + timedelta(
                                    days=int(
                                        self.rng.integers(0, 1500)
                                    )
                                )
                            ).date(),
                            "age_years": int(self.rng.integers(2, 9)),
                            "criticality": self.rng.choice(
                                ["Low", "Medium", "High"],
                                p=[0.25, 0.50, 0.25],
                            ),
                        }
                    )

        self.production_lines = pd.DataFrame(line_rows)
        self.machines = pd.DataFrame(machine_rows)

        product_rows = []

        for product_number in range(1, self.config.number_of_products + 1):
            product_rows.append(
                {
                    "product_id": f"PROD-{product_number:03d}",
                    "product_name": f"Component Product {product_number}",
                    "product_category": self.rng.choice(
                        ["Engine", "Transmission", "Electrical", "Structural"]
                    ),
                    "standard_cycle_time_seconds": int(
                        self.rng.integers(30, 180)
                    ),
                }
            )

        self.products = pd.DataFrame(product_rows)

        supplier_rows = []

        for supplier_number in range(1, self.config.number_of_suppliers + 1):
            supplier_rows.append(
                {
                    "supplier_id": f"SUP-{supplier_number:03d}",
                    "supplier_name": f"Apex Supplier {supplier_number}",
                    "supplier_category": self.rng.choice(
                        ["Metal", "Electronics", "Tools", "Packaging"]
                    ),
                    "supplier_rating": round(
                        float(self.rng.uniform(2.5, 5.0)), 2
                    ),
                }
            )

        self.suppliers = pd.DataFrame(supplier_rows)

        employee_rows = []

        for employee_number in range(1, self.config.number_of_employees + 1):
            employee_rows.append(
                {
                    "employee_id": f"EMP-{employee_number:04d}",
                    "employee_name": f"Employee {employee_number}",
                    "role": self.rng.choice(
                        ["Operator", "Technician", "Supervisor", "Manager"]
                    ),
                    "shift": self.rng.choice(["A", "B", "C"]),
                }
            )

        self.employees = pd.DataFrame(employee_rows)

    def _generate_operational_data(self) -> None:
        """Generate production, sensor, failure, downtime, maintenance, and quality data."""

        production_rows = []
        sensor_rows = []
        failure_rows = []
        downtime_rows = []
        maintenance_rows = []
        quality_rows = []

        start_date = datetime(2026, 1, 1)

        machine_records = self.machines.to_dict("records")
        product_records = self.products.to_dict("records")

        production_id = 1
        sensor_id = 1
        failure_id = 1
        downtime_id = 1
        maintenance_id = 1
        inspection_id = 1

        for machine in machine_records:
            machine_id = machine["machine_id"]
            line_id = machine["line_id"]

            machine_health_factor = float(self.rng.uniform(0.85, 1.0))

            for day_number in range(self.config.number_of_days):
                current_date = start_date + timedelta(days=day_number)

                daily_failure = (
                    self.rng.random()
                    < self.config.failure_probability
                )

                failure_created = False
                failure_reference = None

                if daily_failure:
                    failure_reference = f"FAIL-{failure_id:05d}"

                    failure_rows.append(
                        {
                            "failure_id": failure_reference,
                            "machine_id": machine_id,
                            "failure_date": current_date.date(),
                            "failure_type": self.rng.choice(
                                [
                                    "Overheating",
                                    "Excessive Vibration",
                                    "Electrical Fault",
                                    "Mechanical Wear",
                                ]
                            ),
                            "severity": self.rng.choice(
                                ["Medium", "High", "Critical"],
                                p=[0.45, 0.40, 0.15],
                            ),
                            "failure_description": (
                                "Synthetic machine failure generated "
                                "for testing."
                            ),
                        }
                    )

                    failure_id += 1
                    failure_created = True

                for record_number in range(
                    self.config.records_per_machine_per_day
                ):
                    product = product_records[
                        int(
                            self.rng.integers(
                                0, len(product_records)
                            )
                        )
                    ]

                    planned_quantity = int(self.rng.integers(80, 150))

                    base_efficiency = (
                        machine_health_factor * 100
                    )

                    if failure_created:
                        efficiency = float(
                            self.rng.uniform(45, 70)
                        )
                    else:
                        efficiency = float(
                            np.clip(
                                self.rng.normal(
                                    base_efficiency, 5
                                ),
                                55,
                                100,
                            )
                        )

                    actual_quantity = int(
                        planned_quantity * efficiency / 100
                    )

                    production_rows.append(
                        {
                            "production_record_id": (
                                f"PRODREC-{production_id:07d}"
                            ),
                            "machine_id": machine_id,
                            "line_id": line_id,
                            "product_id": product["product_id"],
                            "production_date": current_date.date(),
                            "shift": self.rng.choice(["A", "B", "C"]),
                            "planned_quantity": planned_quantity,
                            "actual_quantity": actual_quantity,
                            "efficiency_percentage": round(
                                efficiency, 2
                            ),
                        }
                    )

                    production_id += 1

                for reading_number in range(
                    self.config.sensor_readings_per_machine_per_day
                ):
                    timestamp = current_date + timedelta(
                        minutes=reading_number * 240
                    )

                    deterioration = (
                        1.0 - machine_health_factor
                    )

                    temperature = float(
                        self.rng.normal(
                            70 + deterioration * 100,
                            4,
                        )
                    )

                    vibration = float(
                        self.rng.normal(
                            2.0 + deterioration * 8,
                            0.25,
                        )
                    )

                    pressure = float(
                        self.rng.normal(100, 3)
                    )

                    sensor_rows.append(
                        {
                            "sensor_reading_id": (
                                f"SENSOR-{sensor_id:08d}"
                            ),
                            "machine_id": machine_id,
                            "recorded_at": timestamp,
                            "temperature_celsius": round(
                                temperature, 2
                            ),
                            "vibration_mm_s": round(
                                vibration, 3
                            ),
                            "pressure_psi": round(
                                pressure, 2
                            ),
                        }
                    )

                    sensor_id += 1

                if daily_failure:
                    downtime_hours = float(
                        self.rng.uniform(2, 12)
                    )

                    downtime_rows.append(
                        {
                            "downtime_event_id": (
                                f"DOWN-{downtime_id:06d}"
                            ),
                            "machine_id": machine_id,
                            "failure_id": failure_reference,
                            "downtime_date": current_date.date(),
                            "downtime_hours": round(
                                downtime_hours, 2
                            ),
                            "reason": "Machine failure",
                        }
                    )

                    downtime_id += 1

                if (
                    self.rng.random()
                    < self.config.maintenance_probability
                ):
                    maintenance_rows.append(
                        {
                            "maintenance_id": (
                                f"MAINT-{maintenance_id:06d}"
                            ),
                            "machine_id": machine_id,
                            "maintenance_date": current_date.date(),
                            "maintenance_type": self.rng.choice(
                                [
                                    "Preventive",
                                    "Corrective",
                                    "Inspection",
                                ]
                            ),
                            "maintenance_status": "Completed",
                            "technician_id": (
                                f"EMP-{int(self.rng.integers(1, self.config.number_of_employees + 1)):04d}"
                            ),
                            "maintenance_notes": (
                                "Synthetic maintenance activity."
                            ),
                        }
                    )

                    maintenance_id += 1

                if (
                    self.rng.random()
                    < self.config.quality_inspection_probability
                ):
                    defect_probability = (
                        0.02
                        + deterioration * 0.25
                        + (0.15 if daily_failure else 0)
                    )

                    defect_found = (
                        self.rng.random()
                        < defect_probability
                    )

                    quality_rows.append(
                        {
                            "inspection_id": (
                                f"INSP-{inspection_id:07d}"
                            ),
                            "machine_id": machine_id,
                            "product_id": product["product_id"],
                            "inspection_date": current_date.date(),
                            "defect_found": defect_found,
                            "defect_type": (
                                self.rng.choice(
                                    [
                                        "Dimensional Error",
                                        "Surface Defect",
                                        "Assembly Error",
                                    ]
                                )
                                if defect_found
                                else None
                            ),
                            "quality_score": round(
                                float(
                                    self.rng.uniform(70, 100)
                                    if defect_found
                                    else self.rng.uniform(90, 100)
                                ),
                                2,
                            ),
                        }
                    )

                    inspection_id += 1

        self.production_records = pd.DataFrame(production_rows)
        self.sensor_readings = pd.DataFrame(sensor_rows)
        self.machine_failures = pd.DataFrame(failure_rows)
        self.downtime_events = pd.DataFrame(downtime_rows)
        self.maintenance_records = pd.DataFrame(maintenance_rows)
        self.quality_inspections = pd.DataFrame(quality_rows)


def save_datasets(
    datasets: dict[str, pd.DataFrame],
    output_directory: str = "data/raw",
) -> None:
    """Save every generated DataFrame as a CSV file."""

    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)

    for dataset_name, dataframe in datasets.items():
        file_path = output_path / f"{dataset_name}.csv"
        dataframe.to_csv(file_path, index=False)
        print(
            f"Saved {dataset_name}: "
            f"{len(dataframe):,} rows → {file_path}"
        )