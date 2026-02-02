from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

llm=init_chat_model(
    "anthropic:claude-sonnet-4-20250514"
)

class State(TypedDict): #type of info that we want to have 
    messages: Annotated[list,add_messages] #whenever we want to change messages, we use function called add_messages provided by langgraph
    
#define a graph builder which works by using the state
#create a graph which ai agent will use
graph_builder=StateGraph(State)

#create nodes using functions
def chatbot(state:State): #takes a state and returns a modified state or the next state
    return {"messages":[llm.invoke(state["messages"])]}
    #takes the current message and pass it to llm and return new messages, new messages adds to the State
  
graph_builder.add_node("chatbot",chatbot) #adds node

#we need to have a start and end node
#graph is: start->chatbot->end
graph_builder.add_edge(START,end_key="chatbot")
graph_builder.add_edge(start_key="chatbot",end_key=END)

#run graph
graph=graph_builder.compile()

user_input=input("enter a message: ")
state=graph.invoke({"messages":[{"role":"user","content":user_input}]}) #pass a state that we want to start with

# print(state)
# print("------")
print(state["messages"][-1].content)
