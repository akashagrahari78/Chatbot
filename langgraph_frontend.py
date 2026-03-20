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


    response = chatbot.invoke({'messages': [HumanMessage(content = user_input)]}, config=config)
    ai_message = response['messages'][-1].content

    # first add the ai_output to message_history
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    with st.chat_message('assistant'):
        st.text(ai_message)

 