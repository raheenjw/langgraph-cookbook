import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

#utility functions
def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state.thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id, title=None):
    if 'thread_titles' not in st.session_state:
        st.session_state['thread_titles'] = {}
    
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        st.session_state['thread_titles'][thread_id] = title or str(thread_id)

def load_conversation_history(thread_id):
    state = chatbot.get_state(config={'configurable':{'thread_id':thread_id}})
    if state and state.values and 'messages' in state.values:
        return state.values['messages']
    return []


#create session state for message history
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
add_thread(st.session_state.thread_id)

#sidebar
st.sidebar.title("AI Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My Conversations")
if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}

for thread_id in st.session_state['chat_threads'][::-1]:
    title = st.session_state['thread_titles'].get(thread_id, str(thread_id))
    # Truncate title for better UI
    display_name = (title[:30] + '...') if len(title) > 30 else title
    if st.sidebar.button(display_name, key=str(thread_id)):
        st.session_state.thread_id = thread_id
        messages = load_conversation_history(thread_id)
        #becuase message history is in this format in sessions
        temp_messages=[]
        for message in messages:
            if isinstance(message, HumanMessage):
                role="user"
            else:
                role="assistant"
            temp_messages.append({"role": role, "content": message.content})
        st.session_state['message_history'] = temp_messages



#load conversation history
for message in st.session_state.message_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type your query here")
if user_input:
    #first add message to the message_history
    st.session_state['message_history'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)
    CONFIG = {'configurable':{'thread_id':st.session_state.thread_id}}
    #for streaming response
    with st.chat_message('assistant'):
        ai=st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream({"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,stream_mode="messages"))
    st.session_state['message_history'].append({"role": "assistant", "content": ai})
    
    # Update title if it's the first message
    if st.session_state['thread_titles'].get(st.session_state.thread_id) == str(st.session_state.thread_id):
        st.session_state['thread_titles'][st.session_state.thread_id] = user_input
        st.rerun()