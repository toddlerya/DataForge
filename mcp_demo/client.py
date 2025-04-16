# Create server parameters for stdio connection
import asyncio

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# model = ChatOpenAI(model="gpt-4o")

llm = ChatOpenAI(
    api_key="sk-4d586d19af2c40fc9235c7844c89042b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="deepseek-r1-distill-qwen-14b",
)

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["/Users/evi1/Codes/DataForge/mcp_demo/server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(llm, tools)
            agent_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
            print(agent_response)


# Run the async function
asyncio.run(main())
