from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver  #this uses memory in ram

from dotenv import load_dotenv
load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}


checkpointer = MemorySaver()
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)


graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)
chatbot = graph.compile(checkpointer=checkpointer)

# config = {'configurable': {'thread_id': 'thread-1'}}

# response = chatbot.invoke(
#                 {'messages': [HumanMessage(content=' my name is aks')]},
#                 config= config,
#             )

# # this function is used to get state of the chat and used to resume a chat

# chatbot.get_state(config=config).values['messages']
