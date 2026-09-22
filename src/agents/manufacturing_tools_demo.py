from src.agents.tools import (
    get_overall_kpis,
    get_machine_summary,
    get_factory_summary,
    get_machine_sensor_readings,
    get_machine_failures,
    get_machine_downtime,
    get_quality_summary,
    search_manufacturing_knowledge,
    predict_machine_failure,
)


def print_section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()


def main():

    print_section(
        "APEX MANUFACTURING AI - TOOL DEMO"
    )

    # --------------------------------------------------------
    # 1. OVERALL KPIs
    # --------------------------------------------------------

    print_section(
        "1. OVERALL MANUFACTURING KPIs"
    )

    kpis = get_overall_kpis()

    print(
        f"Total production: "
        f"{kpis['total_production']:,.0f}"
    )

    print(
        f"Average efficiency: "
        f"{kpis['average_efficiency']:.2f}%"
    )

    print(
        f"Total downtime: "
        f"{kpis['total_downtime_hours']:.2f} hours"
    )

    print(
        f"Total failures: "
        f"{kpis['total_failures']}"
    )

    print(
        f"Quality inspections: "
        f"{kpis['total_quality_inspections']}"
    )

    print(
        f"Defects: "
        f"{kpis['total_defects']}"
    )

    print(
        f"Average quality score: "
        f"{kpis['average_quality_score']:.2f}"
    )

    # --------------------------------------------------------
    # 2. FACTORIES
    # --------------------------------------------------------

    print_section(
        "2. FACTORY PERFORMANCE"
    )

    factories = get_factory_summary()

    for factory in factories:

        print(
            f"{factory['factory_id']} | "
            f"{factory['factory_name']} | "
            f"Machines: {factory['machine_count']} | "
            f"Production: {factory['total_production']:,.0f} | "
            f"Efficiency: "
            f"{factory['average_efficiency']:.2f}%"
        )

    # --------------------------------------------------------
    # 3. MACHINE
    # --------------------------------------------------------

    print_section(
        "3. MACHINE SUMMARY"
    )

    machines = get_machine_summary()

    for machine in machines[:10]:

        print(
            f"{machine['machine_id']} | "
            f"{machine['machine_name']} | "
            f"Production: "
            f"{machine['total_production']:,.0f} | "
            f"Efficiency: "
            f"{machine['average_efficiency']:.2f}% | "
            f"Failures: "
            f"{machine['failure_count']} | "
            f"Downtime: "
            f"{machine['downtime_hours']:.2f}h"
        )

    # --------------------------------------------------------
    # 4. QUALITY
    # --------------------------------------------------------

    print_section(
        "4. QUALITY"
    )

    quality = get_quality_summary()

    print(
        f"Inspections: "
        f"{quality['total_inspections']}"
    )

    print(
        f"Defects: "
        f"{quality['total_defects']}"
    )

    print(
        f"Average quality score: "
        f"{quality['average_quality_score']:.2f}"
    )

    # --------------------------------------------------------
    # 5. RAG
    # --------------------------------------------------------

    print_section(
        "5. MANUFACTURING KNOWLEDGE SEARCH"
    )

    question = (
        "What should we check when "
        "a machine has high vibration?"
    )

    results = search_manufacturing_knowledge(
        question,
        top_k=2,
    )

    for result in results:

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Section: {result['title']}"
        )

        print(
            f"Similarity: {result['score']:.4f}"
        )

        print()

        print(result["text"])

        print()

    # --------------------------------------------------------
    # 6. ML FAILURE PREDICTION
    # --------------------------------------------------------

    print_section(
        "6. MACHINE FAILURE PREDICTION"
    )

    prediction = predict_machine_failure(
        temperature_celsius=75.0,
        vibration_mm_s=4.5,
        pressure_psi=100.0,
    )

    print(
        f"Failure prediction: "
        f"{prediction['failure_prediction']}"
    )

    print(
        f"Failure probability: "
        f"{prediction['failure_probability']:.4f}"
    )

    print()

    print_section(
        "ALL MANUFACTURING TOOLS WORKING"
    )


if __name__ == "__main__":
    main()