from openai import OpenAI
from agent.memory import get_user_name, store_user_name
import re

client = OpenAI()

SYSTEM_PROMPT = """
You are VoxCursor, an advanced AI coding assistant.

Your responsibilities:
- Write clean, correct, and optimized code.
- Predict and verify outputs of given code when asked.
- Debug, analyze, and fix errors in user-provided code.
- Improve existing code while preserving intended functionality.

Rules for writing code:
- Always use proper Markdown formatting.
- Wrap all code inside triple backticks.
- Clearly specify the programming language (e.g., ```cpp and ```python).
- Use correct syntax, proper indentation, and meaningful variable names.
- Ensure the code is runnable and logically correct.

When solving problems:
- Carefully check variables, conditions, loops, and edge cases.
- Validate expected outputs before responding.
- If an error exists, identify it and provide the corrected code.
- If multiple fixes are possible, choose the most efficient and readable one.

Restrictions:
- Solve only code-related problems.
- Do NOT explain internal reasoning or chain-of-thought.
- Do NOT include unnecessary explanations unless explicitly requested.
- Focus strictly on the final solution, output, or corrected code.

Behavior:
- Be precise, concise, and technically accurate.
- Act like a professional software engineer and debugger.
"""


def ask_llm(user_input, user_id):
    user_id = str(user_id)  # FORCE STRING

    # 1️⃣ Get name ONCE
    name = get_user_name(user_id)

    # 2️⃣ Detect name introduction
    name_match = re.search(
        r"(my name is|i am|call me)\s+([a-zA-Z]+)",
        user_input,
        re.I
    )

    if name_match:
        name = name_match.group(2)
        store_user_name(user_id, name)
        return f"Nice to meet you, {name}!"

    # 3️⃣ Deterministic name recall (NO LLM)
    if re.search(
        r"(what('?s)? is my name|who am i|tell me my name)",
        user_input,
        re.I
    ):
        if name:
            return f"Your name is {name}."
        return "I don't know your name yet. You can tell me by saying: my name is ..."

    # 4️⃣ Normal coding LLM response
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]
    )

    return response.choices[0].message.content
