# app/agent.py
import os
import json
from typing import Any, Dict, Iterator, List, Optional
import logging

from openai import OpenAI

from app.tools import (
    get_user,
    get_medication_by_name,
    check_stock,
    check_prescription,
)

logger = logging.getLogger("pharmacy_agent")
logging.getLogger("httpx").setLevel(logging.WARNING)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# System prompt
# -----------------------------
SYSTEM_PROMPT = """
You are a real-time conversational pharmacy assistant for a retail pharmacy chain.

You are STATELESS: do not assume any memory of past messages beyond the current user message and tool outputs.

Language:
- Answer in the same language as the user (Hebrew or English).

Safety / Policy:
- Provide factual information about medications based on the provided tools. 
- Use ONLY the internal database provided via tools for factual medical information. Do NOT use any other source.
- You MAY explain dosage/usage instructions as general label-style information (non-personalized).
- NO medical advice, NO diagnosis, NO treatment recommendations, NO suitability judgments.
- Do NOT encourage purchasing.
- If the user requests advice (e.g., “what should I take for…”, “is it safe for me?”, “what do you recommend?”),
  refuse briefly and redirect to a pharmacist/doctor.
- Do NOT end your responses with a follow-up question UNLESS a clarifying question is REQUIRED to use the tools.
- If a medication name is provided in Hebrew - When using tools, pass the english translation of the medical name.
- Style: Be concise and final. Avoid offers like “If you’d like, I can…”. Provide the answer and stop.
- Capability limits: Never claim you can check other branches, check locations, set notifications, place orders, reserve items, arrange pickup, or check refill/pickup status.


Tool usage (IMPORTANT):
- For any question about medication details (dosage/usage/safety), stock/availability, or prescription requirements,
  you MUST use the provided tools and not guess.
- If the medication name is missing or ambiguous, ask a short clarifying question.
"""

# -----------------------------
# Tool schemas (Responses API)
# -----------------------------
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "name": "get_medication_by_name",
        "description": "Fetch full factual medication record by exact name (case-insensitive).",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "check_stock",
        "description": "Check current stock quantity for a medication by name (case-insensitive).",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "check_prescription",
        "description": "Combined check: whether medication requires a prescription and whether user has it on file.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "name": {"type": "string"},
            },
            "required": ["user_id", "name"],
        },
    },
]

# -----------------------------
# Tool dispatcher
# -----------------------------
def _run_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "get_medication_by_name":
        return get_medication_by_name(**args)
    if tool_name == "check_stock":
        return check_stock(**args)
    if tool_name == "check_prescription":
        return check_prescription(**args)
    return {"ok": False, "error": {"code": "UNKNOWN_TOOL", "message": f"Tool '{tool_name}' not implemented"}}


def _extract_function_calls(resp: Any) -> List[Dict[str, Any]]:
    """
    Extract function calls from Responses API output.
    Returns list of: {"name": str, "arguments": Any, "call_id": str}
    """
    calls: List[Dict[str, Any]] = []

    output = getattr(resp, "output", None)
    if output is None and isinstance(resp, dict):
        output = resp.get("output")

    if not output:
        return calls

    for item in output:
        itype = getattr(item, "type", None) if not isinstance(item, dict) else item.get("type")
        if itype == "function_call":
            name = getattr(item, "name", None) if not isinstance(item, dict) else item.get("name")
            arguments = getattr(item, "arguments", None) if not isinstance(item, dict) else item.get("arguments")
            call_id = getattr(item, "call_id", None) if not isinstance(item, dict) else item.get("call_id")
            calls.append({"name": name, "arguments": arguments, "call_id": call_id})

    return calls


def _normalize_args(arguments: Any) -> Dict[str, Any]:
    if arguments is None:
        return {}
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except Exception:
            return {}
    return {}


def _looks_hebrew(text: str) -> bool:
    for ch in text or "":
        if "\u0590" <= ch <= "\u05FF":
            return True
    return False


# -----------------------------
# Main agent entry (streaming)
# -----------------------------
def stream_agent_reply(user_id: str, user_message: str) -> Iterator[str]:
    """
    Stateless streaming agent with a mandatory User Gate:
    1) get_user(user_id) ALWAYS runs first
    2) if unknown user -> respond & stop
    3) else use GPT-5 with tool-calling for medication flows
    """

    logger.info("chat_request user_id=%s message=%r", user_id, user_message)

    # ---- Step 0: USER GATE (no model call) ----
    user_res = get_user(user_id)
    if not user_res.get("found"):
        logger.warning("unknown_user user_id=%s", user_id)
        # respond in the user's language based on message
        if _looks_hebrew(user_message):
            yield f"לא מצאתי את המשתמש במערכת (user_id: {user_id}), ולכן לא אוכל להמשיך. אם יש לך user_id אחר, שלחי/שלח אותו בבקשה."
        else:
            yield f"I couldn’t find this user in our system (user_id: {user_id}), so I can’t proceed. Please provide a valid user_id."
        return
    else:
        logger.info("user_ok user_id=%s name=%s", user_id, user_res["user"].get("name"))

    # ---- Step 1: build base input ----
    base_input: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"User context: user_id={user_id}, name={user_res['user'].get('name')}, prescriptions={user_res['user'].get('prescriptions', [])}"},
        {"role": "user", "content": user_message},
    ]

    # ---- Step 2: non-streaming call to decide tool usage ----
    resp = client.responses.create(
        model="gpt-5",
        input=base_input,
        tools=TOOLS,
        tool_choice="auto",
    )

    tool_calls = _extract_function_calls(resp)
    
    logger.info(
        "model_tool_calls count=%d calls=%s",
        len(tool_calls),
        [{"name": c.get("name"), "arguments": c.get("arguments")} for c in tool_calls],
    )


    # ---- Step 3: if no tools, stream direct answer ----
    if not tool_calls:
        with client.responses.stream(model="gpt-5", input=base_input) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    yield event.delta
                if event.type == "response.error":
                    yield "\nSorry — I encountered an error while generating the response."
                    return
        return

    # ---- Step 4: execute tools and build outputs ----

    tool_outputs: List[Dict[str, Any]] = []
    for call in tool_calls:
        name = call.get("name")
        args = _normalize_args(call.get("arguments"))

        # Ensure user_id always present for check_prescription
        if name == "check_prescription" and "user_id" not in args:
            args["user_id"] = user_id

        logger.info("tool_start name=%s args=%s", name, args)

        try:
            result = _run_tool(name, args)
            logger.info(
                "tool_end name=%s ok=%s error_code=%s",
                name,
                result.get("ok", result.get("found")),
                (result.get("error") or {}).get("code"),
            )
        except Exception as e:
            logger.exception("tool_exception name=%s", name)
            result = {"ok": False, "error": {"code": "TOOL_ERROR", "message": str(e)}}

        tool_outputs.append(
            {
                "type": "function_call_output",
                "call_id": call.get("call_id"),
                "output": json.dumps(result),
            }
        )

      # If medication is not found in internal DB — return deterministic message (no model call)
    for out in tool_outputs:
        try:
            result = json.loads(out.get("output", "{}"))
        except Exception:
            continue

        if result.get("error", {}).get("code") == "NOT_FOUND":
            if _looks_hebrew(user_message):
                yield (
                    "מצטער/ת, לא מצאתי את שם התרופה במאגר הפנימי של בית המרקחת, "
                    "ולכן אינני יכול/ה לספק מידע עליה. "
                    "אם תרצה/י, אפשר לבדוק שוב עם איות מדויק (ובאנגלית אם יש), או לציין שם מסחרי."
                )
            else:
                yield (
                    "Sorry — I couldn’t find that medication in our internal pharmacy database, "
                    "so I can’t provide information about it. "
                    "If you’d like, please confirm the exact spelling (and the generic/brand name)."
                )
            return
    
    logger.info("flow_summary user_id=%s tools_used=%s", user_id, [c.get("name") for c in tool_calls])


    # ---- Step 5: stream final answer with tool context ----
    resp_output = getattr(resp, "output", None)
    if resp_output is None and isinstance(resp, dict):
        resp_output = resp.get("output")

    if not resp_output:
        yield "\nSorry — internal error: missing tool call context."
        return

    final_input: List[Dict[str, Any]] = []
    final_input.extend(base_input)
    final_input.extend(resp_output)      # includes the function_call items with call_id
    final_input.extend(tool_outputs)     # outputs referencing those call_id's

    with client.responses.stream(model="gpt-5", input=final_input, tools=TOOLS, tool_choice="none", 
) as stream:
        for event in stream:
            if event.type == "response.output_text.delta":
                yield event.delta
            if event.type == "response.error":
                yield "\nSorry — I encountered an error while generating the response."
                return
