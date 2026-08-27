import json
from pathlib import Path

from app.config.config import settings
from app.llm.client import OllamaClient
from app.models.schemas import ToolCall

CASES_FILE = Path(__file__).parent / "tool_selection_cases.json"


def load_cases():
    with CASES_FILE.open() as file:
        return json.load(file)


def select_tool(client: OllamaClient, user_input: str) -> ToolCall:
    prompt = f"{settings.TOOL_SELECTION_PROMPT}\n{user_input}"

    response = client.generate(prompt, True)

    response = response.replace("```json", "").replace("```", "").strip()

    return ToolCall.model_validate_json(response)


def test_tool_selection_baseline():
    client = OllamaClient()

    cases = load_cases()

    total = len(cases)
    correct_tool = 0
    correct_arguments = 0
    invalid_json = 0

    for case in cases:
        try:
            decision = select_tool(client, case["input"])

        except Exception as error:
            invalid_json += 1

            print(
                f"\n❌ INVALID JSON"
                f"\nID: {case['id']}"
                f"\nInput: {case['input']}"
                f"\nError: {error}"
            )

            continue

        tool_correct = decision.tool == case["expected_tool"]

        arguments_correct = decision.arguments == case["expected_arguments"]

        if tool_correct:
            correct_tool += 1

        if tool_correct and arguments_correct:
            correct_arguments += 1

        status = "✅" if tool_correct and arguments_correct else "❌"

        print(
            f"\n{status} {case['id']}"
            f"\nInput: {case['input']}"
            f"\nExpected tool: {case['expected_tool']}"
            f"\nActual tool: {decision.tool}"
            f"\nExpected arguments: {case['expected_arguments']}"
            f"\nActual arguments: {decision.arguments}"
        )

    print("\n==============================")
    print("TOOL SELECTION BASELINE")
    print("==============================")
    print(f"Total cases:       {total}")
    print(f"Correct tool:      {correct_tool}/{total}")
    print(f"Correct arguments: {correct_arguments}/{total}")
    print(f"Invalid JSON:      {invalid_json}/{total}")

    assert total > 0
