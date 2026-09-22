from src.data_generation.config import GeneratorConfig
from src.data_generation.generator import (
    ManufacturingDataGenerator,
    save_datasets,
)


def main() -> None:
    config = GeneratorConfig()

    generator = ManufacturingDataGenerator(config)
    datasets = generator.generate_all()

    save_datasets(datasets)

    print("\nApex synthetic manufacturing data generation completed.")


if __name__ == "__main__":
    main()