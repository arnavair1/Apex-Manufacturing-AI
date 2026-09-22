import json

from src.agents.tools import AVAILABLE_TOOLS
from src.agents.tool_schemas import TOOL_SCHEMAS
from src.llm.groq_client import ask_groq


SYSTEM_PROMPT = """
You are Apex Manufacturing AI, an evidence-based manufacturing
assistant.

You have access to manufacturing database tools, machine-learning
prediction tools, and a manufacturing knowledge base.

Your job is to answer manufacturing questions using available
evidence.

IMPORTANT RULES:

1. Never invent manufacturing data.

2. Never invent sensor measurements.

3. Never invent production numbers.

4. Never invent failures, downtime, quality results, or maintenance
history.

5. Never invent manufacturer operating limits or safety thresholds.

6. NEVER convert an observed maximum, minimum, average, or recent
sensor value into a safety threshold.

7. NEVER recommend shutdown because a sensor value crossed an
observed historical maximum unless an authoritative manufacturer
limit or other explicitly supplied operating limit supports that
recommendation.

8. If manufacturer operating limits are unavailable, say so.

9. Clearly distinguish:
   - observed database evidence
   - machine-learning predictions
   - knowledge-base guidance
   - interpretation

10. A machine-learning prediction is a model output. It is not proof
that a machine will or will not fail.

11. Knowledge-base information is general manufacturing guidance
unless the database provides machine-specific evidence.

12. If required evidence is unavailable, explicitly say that it is
unavailable.

13. Do not claim that a machine is safe or unsafe without appropriate
evidence.

14. Do not claim that a machine will or will not fail.

15. When investigating a specific machine, use relevant manufacturing
tools instead of guessing.

16. Keep answers concise but useful.

17. When answering a question about a specific machine, mention the
machine ID clearly.

18. If the user asks which machines need attention, use the attention
workflow rather than requesting data for all machines individually.

19. "Needs attention" means that a machine has signals that deserve
further investigation. It does not mean the machine is unsafe or
failing.

20. When giving recommendations, recommend investigation, verification,
maintenance review, sensor validation, trend monitoring, or obtaining
manufacturer specifications when appropriate.

21. Do not create numeric alert values from the data.

22. Do not recommend proactive shutdown solely because a current value
is higher than a previously observed value.

23. If an operational limit is needed but unavailable, explicitly
recommend obtaining the applicable manufacturer or engineering limit
instead of inventing one.
"""


def execute_tool(tool_name, arguments):
    """
    Execute a registered manufacturing tool safely.
    """

    if tool_name not in AVAILABLE_TOOLS:
        return {
            "error": (
                f"Unknown manufacturing tool: {tool_name}"
            )
        }

    tool_function = AVAILABLE_TOOLS[tool_name]

    try:
        return tool_function(**arguments)

    except Exception as error:
        return {
            "error": (
                f"Tool '{tool_name}' failed: "
                f"{type(error).__name__}: {error}"
            )
        }


def is_attention_question(question):
    """
    Detect questions asking which machines need attention.
    """

    question_lower = question.lower()

    attention_phrases = [
        "which machines need attention",
        "which machines need to be checked",
        "which machines need checking",
        "machines need attention",
        "machines need to be checked",
        "machines need checking",
        "machines should we investigate",
        "which machines should we investigate",
        "what machines need attention",
        "what machines should we investigate",
        "machine attention",
        "machines at risk",
        "machines with issues",
        "machines with problems",
    ]

    return any(
        phrase in question_lower
        for phrase in attention_phrases
    )


def safe_float(value, default=0.0):
    """
    Convert a value to float safely.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    """
    Convert a value to int safely.
    """

    try:
        if value is None:
            return default

        return int(value)

    except (TypeError, ValueError):
        return default


def get_machine_id(record):
    """
    Extract a machine ID from different possible result formats.
    """

    if not isinstance(record, dict):
        return None

    possible_keys = [
        "machine_id",
        "id",
        "machine",
    ]

    for key in possible_keys:

        value = record.get(key)

        if value is not None:
            return str(value)

    return None


def get_value(record, *keys, default=None):
    """
    Return the first available value from a dictionary.
    """

    if not isinstance(record, dict):
        return default

    for key in keys:

        if key in record and record[key] is not None:
            return record[key]

    return default


def build_attention_shortlist(
    machine_data,
    limit=5,
):
    """
    Build a compact shortlist from machine attention evidence.

    The ranking uses available signals only. It does not create
    safety thresholds or claim that a machine is unsafe.
    """

    if not isinstance(machine_data, list):
        return []

    candidates = []

    for record in machine_data:

        if not isinstance(record, dict):
            continue

        machine_id = get_machine_id(record)

        if not machine_id:
            continue

        downtime = safe_float(
            get_value(
                record,
                "downtime_hours",
                "total_downtime_hours",
                "downtime",
                default=0,
            )
        )

        failures = safe_int(
            get_value(
                record,
                "failure_count",
                "failures",
                "total_failures",
                default=0,
            )
        )

        efficiency = safe_float(
            get_value(
                record,
                "efficiency_percentage",
                "average_efficiency",
                "efficiency",
                default=100,
            ),
            default=100,
        )

        temperature = safe_float(
            get_value(
                record,
                "temperature_celsius",
                "latest_temperature_celsius",
                "temperature",
                default=0,
            )
        )

        vibration = safe_float(
            get_value(
                record,
                "vibration_mm_s",
                "latest_vibration_mm_s",
                "vibration",
                default=0,
            )
        )

        pressure = safe_float(
            get_value(
                record,
                "pressure_psi",
                "latest_pressure_psi",
                "pressure",
                default=0,
            )
        )

        temperature_deviation = abs(
            temperature - 70
        )

        vibration_deviation = abs(
            vibration - 2
        )

        pressure_deviation = abs(
            pressure - 100
        )

        score = (
            downtime
            + (failures * 10)
            + max(0, 100 - efficiency)
            + temperature_deviation
            + (vibration_deviation * 5)
            + pressure_deviation
        )

        candidates.append(
            {
                "machine_id": machine_id,
                "machine_name": get_value(
                    record,
                    "machine_name",
                    default=None,
                ),
                "machine_type": get_value(
                    record,
                    "machine_type",
                    default=None,
                ),
                "criticality": get_value(
                    record,
                    "criticality",
                    default=None,
                ),
                "efficiency_percentage": efficiency,
                "failure_count": failures,
                "downtime_hours": downtime,
                "temperature_celsius": temperature,
                "vibration_mm_s": vibration,
                "pressure_psi": pressure,
                "attention_score": round(
                    score,
                    3,
                ),
                "original_evidence": record,
            }
        )

    candidates.sort(
        key=lambda item: item["attention_score"],
        reverse=True,
    )

    return candidates[:limit]


def run_attention_workflow(user_question):
    """
    Run the deterministic machine-attention workflow.
    """

    print()
    print(
        "[Workflow] Machine attention workflow started."
    )

    machine_evidence = execute_tool(
        "get_machine_attention_signals",
        {},
    )

    if isinstance(machine_evidence, dict):

        if "error" in machine_evidence:

            print(
                "[Workflow] Could not retrieve machine "
                "attention evidence."
            )

            return (
                "I could not retrieve the machine attention "
                "evidence."
            )

        possible_lists = [
            machine_evidence.get("machines"),
            machine_evidence.get("machine_data"),
            machine_evidence.get("results"),
            machine_evidence.get("data"),
        ]

        machine_data = None

        for possible_list in possible_lists:

            if isinstance(possible_list, list):
                machine_data = possible_list
                break

        if machine_data is None:
            machine_data = []

    elif isinstance(machine_evidence, list):

        machine_data = machine_evidence

    else:

        machine_data = []

    print(
        "[Workflow] Received machine evidence."
    )

    print(
        "[Workflow] Total machine records: "
        f"{len(machine_data)}"
    )

    shortlist = build_attention_shortlist(
        machine_data,
        limit=5,
    )

    print(
        "[Workflow] Shortlisted machines: "
        f"{len(shortlist)}"
    )

    if not shortlist:

        return (
            "No machine evidence was available for "
            "the attention analysis."
        )

    compact_shortlist = []

    for machine in shortlist:

        compact_shortlist.append(
            {
                "machine_id": machine["machine_id"],
                "machine_name": machine["machine_name"],
                "machine_type": machine["machine_type"],
                "criticality": machine["criticality"],
                "efficiency_percentage": (
                    machine["efficiency_percentage"]
                ),
                "failure_count": (
                    machine["failure_count"]
                ),
                "downtime_hours": (
                    machine["downtime_hours"]
                ),
                "temperature_celsius": (
                    machine["temperature_celsius"]
                ),
                "vibration_mm_s": (
                    machine["vibration_mm_s"]
                ),
                "pressure_psi": (
                    machine["pressure_psi"]
                ),
            }
        )

    print(
        "[Workflow] Sending compact shortlist to Groq."
    )

    prompt = f"""
The user asked:

{user_question}

Below is a compact shortlist produced from the manufacturing
database.

SHORTLIST:

{json.dumps(
    compact_shortlist,
    indent=2,
    default=str,
)}

Analyze the supplied evidence.

For each machine:
- identify the machine ID
- summarize the available evidence
- mention relevant efficiency, failures, downtime, and sensor
  information when available
- distinguish observed evidence from interpretation

Do not invent missing information.

Do not create safety thresholds.

Do not call a machine unsafe.

Do not claim a machine will fail.

Explain that "needs attention" means the machine deserves
further investigation based on the available signals.

Finish with a short list of the machines that deserve
further investigation, using their actual machine IDs.
"""

    response = ask_groq(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    answer = response.get(
        "content",
        "The model returned an empty answer.",
    )

    print()
    print(
        "===== MACHINE ATTENTION RESULT ====="
    )
    print()
    print(answer)
    print()

    return answer


def run_agent(
    user_question,
    max_iterations=6,
):
    """
    Run the natural-language manufacturing agent.
    """

    if not user_question or not user_question.strip():

        return (
            "Please enter a manufacturing question."
        )

    user_question = user_question.strip()

    if is_attention_question(user_question):

        return run_attention_workflow(
            user_question
        )

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_question,
        },
    ]

    previous_tool_calls = set()

    for iteration in range(
        1,
        max_iterations + 1,
    ):

        print(
            f"[Agent iteration "
            f"{iteration}/{max_iterations}]"
        )

        response = ask_groq(
            messages=messages,
            temperature=0.2,
            tools=TOOL_SCHEMAS,
        )

        content = response.get(
            "content"
        )

        tool_calls = response.get(
            "tool_calls",
            [],
        )

        if not tool_calls:

            print(
                "[Agent] Final answer generated."
            )

            return content or (
                "The model returned an empty answer."
            )

        messages.append(
            {
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls,
            }
        )

        new_tool_call_found = False

        for tool_call in tool_calls:

            tool_call_id = tool_call.get(
                "id",
                "",
            )

            function_data = tool_call.get(
                "function",
                {},
            )

            function_name = function_data.get(
                "name",
                "",
            )

            raw_arguments = function_data.get(
                "arguments",
                "{}",
            )

            call_signature = (
                function_name,
                raw_arguments,
            )

            if call_signature in previous_tool_calls:

                print(
                    "[Agent] Duplicate tool call detected."
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(
                            {
                                "error": (
                                    "This exact tool call "
                                    "was already executed. "
                                    "Use the previous result "
                                    "to answer the user."
                                )
                            }
                        ),
                    }
                )

                continue

            previous_tool_calls.add(
                call_signature
            )

            new_tool_call_found = True

            try:

                arguments = json.loads(
                    raw_arguments
                )

            except json.JSONDecodeError:

                arguments = {}

                tool_result = {
                    "error": (
                        "The model produced invalid "
                        "JSON tool arguments."
                    )
                }

            else:

                print(
                    "[Agent] Tool call: "
                    f"{function_name}"
                )

                print(
                    "[Agent] Arguments: "
                    f"{arguments}"
                )

                tool_result = execute_tool(
                    function_name,
                    arguments,
                )

            try:

                serialized_result = json.dumps(
                    tool_result,
                    default=str,
                )

            except Exception:

                serialized_result = str(
                    tool_result
                )

            max_tool_result_chars = 12000

            if len(serialized_result) > (
                max_tool_result_chars
            ):

                serialized_result = (
                    serialized_result[
                        :max_tool_result_chars
                    ]
                    + "\n...[tool result truncated]"
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": serialized_result,
                }
            )

        if not new_tool_call_found:

            print(
                "[Agent] No new tool calls available."
            )

            final_response = ask_groq(
                messages=messages,
                temperature=0.2,
            )

            return final_response.get(
                "content",
                "The model returned an empty answer.",
            )

    return (
        "The agent reached its maximum number of "
        "tool-calling iterations before producing "
        "a final answer."
    )


def run_chat():
    """
    Interactive natural-language manufacturing assistant.
    """

    print()
    print("=" * 60)
    print("        APEX MANUFACTURING AI")
    print("        NATURAL-LANGUAGE AGENT")
    print("=" * 60)
    print()

    print(
        "Ask a manufacturing question in normal language."
    )

    print(
        "Type 'exit' to quit."
    )

    print()

    while True:

        try:

            user_question = input(
                "You: "
            ).strip()

        except (EOFError, KeyboardInterrupt):

            print()
            print(
                "Exiting Apex Manufacturing AI."
            )
            print()
            break

        if not user_question:
            print()
            continue

        if user_question.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print()
            print(
                "Exiting Apex Manufacturing AI."
            )
            print()
            break

        print()

        try:

            answer = run_agent(
                user_question
            )

        except Exception as error:

            print()
            print(
                "Agent error:"
            )

            print(
                f"{type(error).__name__}: {error}"
            )

            print()

            continue

        print()
        print("===== APEX AI =====")
        print()
        print(answer)
        print()


if __name__ == "__main__":

    run_chat()