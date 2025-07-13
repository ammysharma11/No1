"""
Assistant node – takes receiver & subject directly from state.
"""
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .tools import divide, extract_text, send_html_email

# ───────────  shared state  ────────────────────────────────────────────
class AgentState(TypedDict):
    input_file: Optional[str]
    receiver:   Optional[str]
    subject:    Optional[str]
    messages:   Annotated[list[AnyMessage], add_messages]

# ───────────  LLM with tools  ──────────────────────────────────────────
llm   = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.3)
tools = [divide, extract_text, send_html_email]
llm_t = llm.bind_tools(tools=tools, parallel_tool_calls=False)

# ───────────  assistant node  ─────────────────────────────────────────
def assistant(state: AgentState) -> AgentState:
    receiver = state.get("receiver")
    subject  = state.get("subject") or "No subject"

    if not receiver:
        # stop early – frontend guarantees this but keep the guard
        err = SystemMessage(content="❌ Receiver email missing.")
        return {**state, "messages": state["messages"] + [err]}

    sys = SystemMessage(
        content=(
            "You are a helpful agent with these tools:\n"
            "- extract_text(img_path)\n"
            "- divide(a,b)\n"
            "- send_html_email(html_body, receiver, subject)\n\n"
            f"Current image: {state.get('input_file')}\n"
            f"Receiver: {receiver}\nSubject: {subject}\n"
            "Always call send_html_email with these exact receiver/subject."
        )
    )

    reply = llm_t.invoke([sys] + state["messages"])

    return {
        "messages"  : state["messages"] + [reply],
        "input_file": state["input_file"],
        "receiver"  : receiver,
        "subject"   : subject,
    }
