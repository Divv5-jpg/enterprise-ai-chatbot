from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import asyncio

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

# Tools
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def calculator(
    first_num: float,
    second_num: float,
    operation: str
) -> dict:
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
            return {
                "error": f"Unsupported operation '{operation}'"
            }

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol.
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=YOUR_API_KEY"

    r = requests.get(url)

    return r.json()


tools = [
    get_stock_price,
    calculator,
    search_tool
]

llm_with_tools = llm.bind_tools(tools)


class chatstate(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def build_graph():

    async def chat_node(state: chatstate):

        messages = state['messages']

        response = await llm_with_tools.ainvoke(messages)

        return {
            'messages': [response]
        }

    tool_node = ToolNode(tools)

    graph = StateGraph(chatstate)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    graph.add_conditional_edges(
        "chat_node",
        tools_condition
    )

    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()

    return chatbot


async def main():

    chatbot = build_graph()

    result = await chatbot.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="What is the share price of Apple"
                )
            ]
        }
    )

    print(result['messages'][-1].content)


if __name__ == '__main__':
    asyncio.run(main())