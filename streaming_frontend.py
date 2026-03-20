import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

config = {'configurable': {'thread_id': 'thread-1'}}


# st have component called 'session_state' which is dictionary and does not erase its content when enter is pressed
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []


# loading the conversation history
for message in st.session_state['message_history']:
    st.chat_message(message['role'])
    st.text(message['content'])


user_input = st.chat_input('type here')

if user_input:

    # first add the user_input to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})

    with st.chat_message('user'):
        st.text(user_input)


    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= {'configurable': {'thread_id': 'thread-1'}},
                stream_mode= 'messages'
            )
        )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})