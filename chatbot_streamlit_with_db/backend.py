from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

import requests
import random
import sqlite3

# CONFIG = {'configurable':{'thread_id':'thread-1'}}

llm = ChatOllama(model="llama3.2")

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

# Make tool list
tools = [get_stock_price, search_tool, calculator]

# Make the LLM tool-aware
llm_with_tools = llm.bind_tools(tools)

class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm_with_tools.invoke(messages)

    # response store state
    return {'messages': [response]}

tool_node = ToolNode(tools)

connection = sqlite3.connect('chatbot_streamlit_with_db/chat_history.db',check_same_thread=False) #creates a db behind the scenes,works in a single thread
checkpointer = SqliteSaver(conn=connection)#to store the chat history, connect
graph = StateGraph(ChatState)

# add nodes
graph=StateGraph(ChatState)
graph.add_node("chat_node",chat_node)
graph.add_node("tools",tool_node)

graph.add_edge(START,"chat_node")
# If the LLM asked for a tool, go to ToolNode; else finish
graph.add_conditional_edges("chat_node", tools_condition)

graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)

#to get all chat threads checkpointsfrom db
def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)

# print(all_threads)


# for message_chunk, metadata in chatbot.stream( #instead of invoking the chatbot, we are streaming the response, do in frontend
#     {"messages": [HumanMessage(content="Hello, how are you?")]},config=CONFIG,stream_mode="messages"):
#     if message_chunk.content:
#         print(message_chunk.content, end="", flush=True)
 
#to get all messages for a thread id 
# response = chatbot.invoke({"messages": [HumanMessage(content="Hello, how are you?")]},config=CONFIG)
# print(response)
# chatbot.get_state(config=CONFIG).values['messages']
