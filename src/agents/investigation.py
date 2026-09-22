import json

from src.agents.tools import (
    get_machine_summary,
    get_machine_sensor_readings,
    get_machine_failures,
    get_machine_downtime,
    get_quality_summary,
    search_manufacturing_knowledge,
    predict_machine_failure,
)

from src.llm.groq_client import ask_groq


def get_latest_sensor(sensor_data):
    """
    Extract the latest sensor reading from the
    sensor tool result.
    """

    if isinstance(sensor_data, list):

        if sensor_data:
            return sensor_data[-1]

        return None

    if isinstance(sensor_data, dict):

        readings = sensor_data.get(
            "readings",
            []
        )

        if readings:
            return readings[-1]

    return None


def investigate_machine(machine_id):
    """
    Collect all available evidence for one machine.
    """

    print()
    print("===== MACHINE INVESTIGATION =====")

    print(
        f"[Investigation] Machine: {machine_id}"
    )

    print(
        "[Investigation] Getting machine summary..."
    )

    machine_summary = get_machine_summary(
        machine_id
    )

    print(
        "[Investigation] Getting sensor readings..."
    )

    sensor_data = get_machine_sensor_readings(
        machine_id
    )

    print(
        "[Investigation] Getting failure history..."
    )

    failure_data = get_machine_failures(
        machine_id
    )

    print(
        "[Investigation] Getting downtime history..."
    )

    downtime_data = get_machine_downtime(
        machine_id
    )

    print(
        "[Investigation] Getting quality information..."
    )

    quality_data = get_quality_summary(
        machine_id=machine_id
    )

    print(
        "[Investigation] Searching manufacturing knowledge..."
    )

    knowledge_data = search_manufacturing_knowledge(
        "machine condition monitoring "
        "high vibration temperature pressure "
        "maintenance failure troubleshooting"
    )

    print(
        "[Investigation] Running ML failure prediction..."
    )

    latest_sensor = get_latest_sensor(
        sensor_data
    )

    prediction_data = None

    if latest_sensor:

        temperature = latest_sensor.get(
            "temperature_celsius"
        )

        vibration = latest_sensor.get(
            "vibration_mm_s"
        )

        pressure = latest_sensor.get(
            "pressure_psi"
        )

        if (
            temperature is not None
            and vibration is not None
            and pressure is not None
        ):

            prediction_data = predict_machine_failure(
                temperature_celsius=float(
                    temperature
                ),
                vibration_mm_s=float(
                    vibration
                ),
                pressure_psi=float(
                    pressure
                ),
            )

    evidence = {
        "machine_id":
            machine_id,

        "machine_summary":
            machine_summary,

        "sensor_data":
            sensor_data,

        "failure_history":
            failure_data,

        "downtime_history":
            downtime_data,

        "quality":
            quality_data,

        "knowledge":
            knowledge_data,

        "ml_prediction":
            prediction_data,
    }

    print(
        "[Investigation] Evidence collected."
    )

    return evidence


def build_investigation_prompt(evidence):
    """
    Build a strict evidence-based investigation prompt.
    """

    evidence_json = json.dumps(
        evidence,
        indent=2,
        default=str,
    )

    return f"""
You are an AI manufacturing investigation assistant.

Investigate ONE manufacturing machine using ONLY
the evidence provided below.

==================================================
STRICT EVIDENCE POLICY
==================================================

This is an evidence-based manufacturing system.

You MUST follow these rules.

1. Never invent facts.

2. Never invent measurements.

3. Never invent sensor thresholds.

4. Never invent manufacturer specifications.

5. Never invent operating limits.

6. Never create alert values from observed maxima.

7. Never describe an observed range as "normal",
   "safe", "acceptable", "typical", or "within limits"
   unless the supplied evidence explicitly provides
   the corresponding reference standard or limit.

8. Never create a threshold by adding a number to
   an observed maximum or minimum.

9. Never convert historical observations into safety
   limits.

10. Never claim that the machine is safe.

11. Never claim that the machine is unsafe unless
    the supplied evidence explicitly supports that.

12. Never claim that the machine will fail.

13. Never claim that the machine cannot fail.

==================================================
OBSERVED DATA
==================================================

Values directly supplied by the database are
observations.

Examples include:

- temperature
- vibration
- pressure
- production
- efficiency
- failures
- downtime
- quality

Observed values describe what happened in the
dataset.

They do NOT automatically establish whether a value
is safe, unsafe, normal, abnormal, high, or low.

==================================================
SENSOR INTERPRETATION
==================================================

For temperature, vibration and pressure:

Report the actual observed measurements.

You may report:

- minimum
- maximum
- latest value
- average

ONLY when those values are present in the evidence.

If manufacturer limits are not provided, say:

"No manufacturer operating limit was provided,
so the observed value cannot be classified against
a formal equipment limit."

Do NOT create example thresholds.

For example, NEVER write:

"Alert above 83 °C."

unless 83 °C is explicitly supplied as a valid
threshold in the evidence.

==================================================
MACHINE LEARNING
==================================================

The ML model uses:

- temperature
- vibration
- pressure

The ML output is statistical model output.

It is NOT proof of failure.

It is NOT proof that failure is impossible.

If failure_probability is 0.0%, say that the model
returned 0.0%.

Do NOT translate this into:

"zero real-world risk"

or:

"failure is impossible."

The model was trained using this project's synthetic
manufacturing dataset.

Therefore, treat the prediction as supporting
evidence rather than a definitive diagnostic result.

==================================================
KNOWLEDGE BASE
==================================================

The knowledge base contains general manufacturing
guidance.

Use it as supporting context.

Do not transform general recommendations into
machine-specific facts.

If the knowledge base mentions possible causes,
describe them as possible causes.

Do not claim that any particular cause is present
unless the machine evidence demonstrates it.

==================================================
REPORT FORMAT
==================================================

Use exactly this structure.

===== MACHINE INVESTIGATION =====

Machine:
Machine type:
Criticality:

===== PRODUCTION =====

Report the available production evidence.

===== SENSOR CONDITION =====

Report the available:

- temperature
- vibration
- pressure

Report actual observed values.

If no formal limits are provided, explicitly say so.

Do not invent thresholds.

===== FAILURE HISTORY =====

Report recorded failures.

If none exist in the supplied dataset, say:

"No recorded failures were found in the supplied
dataset."

Do not claim this proves the machine has never
failed outside the dataset.

===== DOWNTIME =====

Report recorded downtime.

If none exists, say:

"No recorded downtime was found in the supplied
dataset."

===== QUALITY =====

Report:

- inspection count
- defect count
- quality score
- defect types if available

Do not claim that zero recorded defects means
zero defects occurred outside the dataset.

===== ML FAILURE PREDICTION =====

Report:

- failure_prediction
- failure_probability
- model features

Then explicitly state:

"This is a machine-learning model output and is not
proof that a failure will or will not occur."

===== KNOWLEDGE BASE =====

Summarize relevant manufacturing guidance.

===== INVESTIGATION ASSESSMENT =====

Combine the evidence.

Clearly separate:

OBSERVATION

from

INTERPRETATION.

Do not call sensor values normal or abnormal unless
the evidence provides an appropriate reference.

If the evidence is insufficient, say:

"Insufficient evidence to determine this."

===== RECOMMENDED INVESTIGATION =====

Give practical next steps.

Appropriate recommendations can include:

- obtain manufacturer operating limits
- review sensor trends
- validate sensor calibration
- review maintenance history
- inspect relevant components
- review quality trends
- investigate changes over time

Do NOT create numeric alert thresholds.

==================================================
MACHINE EVIDENCE
==================================================

{evidence_json}
"""


def generate_investigation_report(machine_id):
    """
    Run the complete machine investigation.
    """

    evidence = investigate_machine(
        machine_id
    )

    prompt = build_investigation_prompt(
        evidence
    )

    print(
        "[Investigation] Sending evidence to Groq..."
    )

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    result = ask_groq(
        messages
    )

    answer = result.get(
        "content"
    )

    print()

    if answer:

        print(answer)

    else:

        print(
            "Groq returned no investigation report."
        )

    print()
    print(
        "===== END OF INVESTIGATION ====="
    )
    print()


if __name__ == "__main__":

    print()
    print(
        "===== APEX MACHINE INVESTIGATOR ====="
    )

    machine_id = input(
        "Enter machine ID to investigate: "
    ).strip()

    if not machine_id:

        print(
            "No machine ID provided."
        )

    else:

        generate_investigation_report(
            machine_id
        )