from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from .tools import divide, extract_text, send_html_email
from .agent import assistant, AgentState

tools = [divide, extract_text, send_html_email]

builder = StateGraph(AgentState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

react_graph = builder.compile()
