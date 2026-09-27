from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
import sqlite3
import os 
from dotenv import load_dotenv
load_dotenv()
print("Tracing:", os.getenv("LANGCHAIN_TRACING_V2"))
print("Project:", os.getenv("LANGCHAIN_PROJECT"))
print("LangSmith key:", os.getenv("LANGCHAIN_API_KEY") is not None)
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)
class chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:chatstate):
    messages=state['messages']
    response=llm.invoke(messages)
    return {'messages':[response]}
conn = sqlite3.connect(
    database='chatbot.db',
    check_same_thread=False
)
checkpointer = SqliteSaver(conn)
graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)
chatbot=graph.compile(checkpointer=checkpointer)
def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return (list(all_threads))