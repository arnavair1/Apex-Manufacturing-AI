from src.agents.groq_agent import run_attention_workflow
from src.agents.investigation import generate_investigation_report


def show_header():
    print()
    print("=" * 60)
    print("        APEX MANUFACTURING AI")
    print("=" * 60)
    print()


def show_menu():
    print("Choose an action:")
    print()
    print("1. Find machines that need attention")
    print("2. Investigate a specific machine")
    print("3. Exit")
    print()


def get_choice():
    return input("Enter your choice: ").strip()


def attention_workflow():
    print()
    print("=" * 60)
    print("        MACHINE ATTENTION ANALYSIS")
    print("=" * 60)
    print()

    user_question = (
        "Which machines need attention based on the "
        "available manufacturing evidence?"
    )

    run_attention_workflow(user_question)

    print()
    print("=" * 60)
    print("        END OF ATTENTION ANALYSIS")
    print("=" * 60)
    print()


def investigation_workflow():
    print()
    print("=" * 60)
    print("        MACHINE INVESTIGATION")
    print("=" * 60)
    print()

    machine_id = input(
        "Enter the machine ID "
        "(example: MCH-005-03-01): "
    ).strip()

    if not machine_id:
        print()
        print("No machine ID was provided.")
        return

    print()
    print(f"Starting investigation for: {machine_id}")
    print()

    generate_investigation_report(machine_id)


def main():
    show_header()

    while True:

        show_menu()

        choice = get_choice()

        if choice == "1":

            attention_workflow()

            print()
            investigate = input(
                "Would you like to investigate a specific "
                "machine now? (y/n): "
            ).strip().lower()

            if investigate == "y":
                investigation_workflow()

        elif choice == "2":

            investigation_workflow()

        elif choice == "3":

            print()
            print("Exiting Apex Manufacturing AI.")
            print()
            break

        else:

            print()
            print(
                "Invalid choice. "
                "Please enter 1, 2, or 3."
            )
            print()


if __name__ == "__main__":
    main()