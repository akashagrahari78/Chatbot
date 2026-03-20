from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage,HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver  #this uses memory in ram
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


# --------------------------------------------------------tools-----------------------------------
#tools

search_tool = DuckDuckGoSearchRun(region = 'us-en')

@tool
def calculator(a : float, b : float, operation : str) -> dict:
    '''perform a basic arithmetic operation on two numbers. Supported operations: add, sub, mul, div'''
    try:
        if operation == 'add':
            result = a + b
        elif operation == 'sub':
            result = a-b
        elif operation == 'mul':
            result = a*b
        elif operation == 'div':
            if b == 0:
                return {'error': 'division by zero is not allowed'}
            result = a/b
        else:
            return {'error': f"unsupported operation: {operation}"}
        
        return {'a ': a, 'b': b, 'operation': operation, "result": result}
    except Exception as e:
        return {'error': str(e)}
    
 
ALPHA_VANTAGE_API_KEY = "YOUR_API_KEY"


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'TSLA') using Alpha Vantage API.
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"

    response = requests.get(url)
    data = response.json()

    try:
        price_data = data["Global Quote"]

        return {
            "symbol": price_data["01. symbol"],
            "price": price_data["05. price"],
            "change": price_data["09. change"],
            "change_percent": price_data["10. change percent"]
        }

    except Exception:
        return {"error": "Could not fetch stock price"}
    

# make tool list
tools = [get_stock_price, search_tool, calculator]

# make the llm tools-aware
llm_with_tools = llm.bind_tools(tools)


# -------------------------------------------------

class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]



# -------------------------------------------------nodes and edges---------------------------
def chat_node(state: ChatState):

    # take user query from state
    messages = state['messages']

    # send to llm
    response = llm.invoke(messages)

    # response store state
    return {'messages': [response]}


tool_node = ToolNode(tools)


# -------------------------------------------------checkpointers--------------------------------------
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)



# -------------------------------------------------Graph
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)


graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)
chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    
    return list(all_threads)


# config = {'configurable': {'thread_id': 'thread-1'}}
# response = chatbot.invoke(
#                 {'messages': [HumanMessage(content='what is  my name')]},
#                 config= config,
#             )
# print(response)

# # this function is used to get state of the chat and used to resume a chat

# chatbot.get_state(config=config).values['messages']
