from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver 
from langgraph.graph.message import add_messages


# CONFIG = {'configurable':{'thread_id':'thread-1'}}

llm = ChatOllama(model="llama3.2")


class ChatState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}

checkpointer = InMemorySaver()#to store the chat history
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

chatbot = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in chatbot.stream( #instead of invoking the chatbot, we are streaming the response, do in frontend
#     {"messages": [HumanMessage(content="Hello, how are you?")]},config=CONFIG,stream_mode="messages"):
#     if message_chunk.content:
#         print(message_chunk.content, end="", flush=True)
 
#to get all messages for a thread id 
# chatbot.invoke({"messages": [HumanMessage(content="Hello, how are you?")]},config=CONFIG)
# chatbot.get_state(config=CONFIG).values['messages']