#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/16 16:49 
# @Author   : guoqun X2590
# @FileName : demo_client.py
# @Project  : PreviewDataForge

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
import asyncio

from utils.llm_util import llm_client

server_params = StdioServerParameters(
    command="python",
    args=[r"F:\GITLAB\PreviewDataForge\mcp_server\mcp_demo.py"]
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm_client, tools)
            agent_response = await agent.ainvoke({"messages": "what's (4*5) x 12?, you should use tool calc!"})
            print(agent_response)


asyncio.run(main())
