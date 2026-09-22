import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


if not GROQ_API_KEY:

    raise RuntimeError(
        "GROQ_API_KEY was not found. "
        "Add it to the project's .env file."
    )


client = Groq(
    api_key=GROQ_API_KEY
)


MODEL_NAME = "openai/gpt-oss-120b"


def ask_groq(
    messages,
    temperature=0.2,
    tools=None,
):
    """
    Send a request to Groq.

    Returns the complete assistant message so that
    the agent can inspect both normal responses and
    tool calls.
    """

    request_parameters = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
    }

    if tools:

        request_parameters["tools"] = tools

        request_parameters[
            "tool_choice"
        ] = "auto"


    response = client.chat.completions.create(
        **request_parameters
    )


    message = response.choices[0].message


    return {
        "content": message.content,
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in (
                message.tool_calls or []
            )
        ],
    }


if __name__ == "__main__":

    print(
        "===== GROQ TEST ====="
    )

    messages = [
        {
            "role": "user",
            "content": (
                "Explain what a manufacturing "
                "production line is in two sentences."
            ),
        }
    ]

    result = ask_groq(
        messages
    )

    print()

    print(
        result["content"]
    )