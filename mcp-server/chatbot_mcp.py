## client->server
# Chatbot that uses the expense tracker MCP server (add/list/summarize expenses).

import os
import asyncio
from datetime import date
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOllama(model="llama3.2")

# Path to expense tracker MCP server (portable: relative to this script)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPENSE_TRACKER_SCRIPT = os.path.join(_SCRIPT_DIR, "expense_tracker.py")

# MCP client for local FastMCP expense tracker
client = MultiServerMCPClient(
    {
        "expense": {
            "transport": "stdio",
            "command": "python3",
            "args": [EXPENSE_TRACKER_SCRIPT],
        },
    }
)

# System prompt so the LLM knows how to use expense tools and date format
EXPENSE_SYSTEM_PROMPT = """You are a helpful assistant. You have tools to add, list, and summarize expenses other than chatting with the user.

- **Dates**: Always use YYYY-MM-DD. For "today" use {today}.
- **add_expense(date, amount, category, subcategory="", note="")**: Use for phrases like "add ₹500 for udemy", "spent ₹200 on groceries". Infer a sensible category (e.g. Education, Food) and put details in note.
- **list_expenses(start_date, end_date)**: List expenses in an inclusive date range.
- **summarize(start_date, end_date, category=None)**: Summarize totals by category in a date range; category is optional.

Prefer these categories when adding expenses: Food, Transport, Shopping, Entertainment, Bills, Health, Education, Travel, Personal, Other. Use the note field for specifics (e.g. "udemy course", "metro")."""


class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

async def build_graph(verbose=False):
        tools = await client.get_tools()
        if verbose:
            print("Loaded tools:", [t.name for t in tools])

        llm_with_tools = llm.bind_tools(tools)

        #add node as async function
        async def chat_node(state: ChatState):
            messages = state['messages']
            response = await llm_with_tools.ainvoke(messages)
            return {'messages': [response]}

        tool_node = ToolNode(tools) #internally async

        graph = StateGraph(ChatState)

        # add nodes
        graph=StateGraph(ChatState)
        graph.add_node("chat_node",chat_node)
        graph.add_node("tools",tool_node)


        graph.add_edge(START,"chat_node")
        # If the LLM asked for a tool, go to ToolNode; else finish
        graph.add_conditional_edges("chat_node", tools_condition)

        graph.add_edge("tools", "chat_node")

        chatbot = graph.compile()
        return chatbot

async def main():
    chatbot = await build_graph(verbose=True)
    system_msg = SystemMessage(
        content=EXPENSE_SYSTEM_PROMPT.format(today=date.today().isoformat())
    )

    print("Expense tracker ready. Examples: 'add 500 for udemy course', 'list expenses this week', 'summarize January' (type 'exit' to quit).\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        response = await chatbot.ainvoke({
            "messages": [system_msg, HumanMessage(content=user_input)]
        })
        print(f"Bot: {response['messages'][-1].content}\n")
        # result=await chatbot.ainvoke({"messages": [HumanMessage(content="add an expense- rs 500 for udemy course")]})
        # print(result["messages"][-1].content) 

if __name__ == "__main__":
    asyncio.run(main())