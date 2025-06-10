import asyncio
import json
import os
import time
from typing import Annotated, List, Optional, TypedDict

import chainlit as cl
import pandas as pd
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

# --- 环境变量配置 ---
# 请确保在您的环境中设置了 OPENAI_API_KEY 和 OPENAI_BASE_URL
# 例如，在终端中运行:
# export OPENAI_API_KEY="your_key_here"
# export OPENAI_BASE_URL="your_base_url_here" # 如果使用代理

# --- 1. 定义LLM和重试配置 ---
MAX_RETRIES = 5  # 最大重试次数

# 初始化LLM模型
# temperature=0 表示我们希望LLM的输出更具确定性
llm = ChatOpenAI(
    base_url=os.getenv("SILICONFLOW_BASE_URL"),
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    # 关键参数：通过extra_body关闭think功能
    # model="Qwen/Qwen3-8B",
    # model="qwen3-30b-a3b",
    # model="qwen3-8b",
    # model="Qwen3-30B-A3B",
    # model="DeepSeek-R1-Distill-Qwen-14B-AWQ",
    # model="fiberhome-chat",
    # model="DeepSeek-R1-Distill-Qwen-32B",
    # model="Qwen/Qwen3-8B",
    model="Qwen/Qwen3-30B-A3B",
    # model="Qwen/Qwen3-235B-A22B",
    temperature=0.4,
    # top_p=0.95,
)


# --- 2. 模拟外部服务 ---


def mock_db_query(table_name: str) -> dict:
    """
    模拟数据库查询，返回表的元数据。
    在真实场景中，这里会连接到实际的数据库并执行查询。
    """
    print(f"--- 模拟数据库查询: {table_name} ---")
    time.sleep(1)  # 模拟网络延迟
    schemas = {
        "users": {
            "description": "用户信息表",
            "name": "users",  # 在 generate_config_node 中被引用
            "columns": [
                {
                    "name": "id",
                    "type": "int",
                    "primary_key": True,
                    "description": "用户ID",
                },
                {"name": "name", "type": "varchar", "description": "用户姓名"},
                {"name": "age", "type": "int", "description": "用户年龄"},
                {"name": "email", "type": "varchar", "description": "电子邮箱"},
                {"name": "created_at", "type": "datetime", "description": "创建时间"},
            ],
        },
        "orders": {
            "description": "订单信息表",
            "name": "orders",  # 在 generate_config_node 中被引用
            "columns": [
                {
                    "name": "order_id",
                    "type": "int",
                    "primary_key": True,
                    "description": "订单ID",
                },
                {"name": "user_id", "type": "int", "description": "关联的用户ID"},
                {"name": "product_name", "type": "varchar", "description": "产品名称"},
                {"name": "amount", "type": "decimal", "description": "订单金额"},
                {"name": "order_date", "type": "date", "description": "下单日期"},
            ],
        },
    }
    return schemas.get(table_name.lower(), None)


async def mock_data_engine_service(config_json: dict) -> str:
    """
    模拟数据生成引擎服务。
    接收JSON配置，模拟执行数据生成任务，并返回结果URL。
    """
    print(
        f"--- 模拟调用数据生成引擎，配置: {json.dumps(config_json, indent=2, ensure_ascii=False)} ---"
    )
    await cl.Message(
        content="✅ 配置已提交至数据生成引擎，正在生成数据... (模拟耗时3秒)"
    ).send()
    await asyncio.sleep(3)
    return "https://example.com/generated_data/result_12345.csv"


# --- 3. LangGraph状态定义 ---


class StructuredIntent(BaseModel):
    """结构化用户意图"""

    table_name: str = Field(description="用户想要操作的数据库表名")
    constraints: str = Field(description="用户对生成数据的具体要求和约束条件")
    num_rows: int = Field(description="期望生成的数据行数")


class GraphState(TypedDict):
    """
    定义图（Graph）的状态。
    所有节点之间通过这个状态对象传递数据。
    """

    user_initial_intent: str  # 用户的原始输入
    structured_intent: Optional[StructuredIntent]  # LLM解析后的结构化意图
    user_feedback: Optional[str]  # 用户在审核阶段的反馈
    table_schema: Optional[dict]  # 从数据库查询到的表元数据
    generation_config_json: Optional[dict]  # LLM生成的配置JSON
    result_url: Optional[str]  # 最终生成的数据下载链接
    error_message: Optional[str]  # 流程中发生的错误信息
    retry_count: int  # 当前重试次数


# --- 4. LangGraph 节点定义 ---


@cl.step(name="1. 意图识别 (LLM)", type="llm")
async def intent_recognition_node(state: GraphState):
    """
    使用LLM识别用户的意图，并结构化输出。
    包含重试机制。
    """
    state["retry_count"] = 0
    state["error_message"] = None
    prompt = f"""
    你是一个任务规划专家。请根据用户输入的自然语言，解析出核心的任务参数。
    用户的输入是：'{state['user_initial_intent']}'
    用户的反馈是：'{state.get('user_feedback', '无')}'
    请将解析结果以JSON格式输出。
    """

    while state["retry_count"] < MAX_RETRIES:
        try:
            structured_llm = llm.with_structured_output(StructuredIntent)
            intent = await structured_llm.ainvoke(prompt)
            state["structured_intent"] = intent
            state["user_feedback"] = None  # 清空反馈
            return state
        except Exception as e:
            state["retry_count"] += 1
            await cl.Message(
                content=f"意图识别失败，正在进行第 {state['retry_count']}/{MAX_RETRIES} 次重试... 错误: {e}"
            ).send()
            await asyncio.sleep(1)  # 等待1秒后重试

    state["error_message"] = f"意图识别在重试{MAX_RETRIES}次后仍然失败。"
    return state


@cl.step(name="审查意图参数")
async def intent_review_node(state: GraphState):
    """
    中断流程，让人工审查LLM提取的参数。
    """
    if state.get("error_message"):
        return state

    intent = state["structured_intent"]
    review_msg = f"""
    请您审查以下由系统识别出的任务参数：
    - **表名称**: `{intent.table_name}`
    - **约束条件**: `{intent.constraints}`
    - **生成条数**: `{intent.num_rows}`

    如果参数正确，请输入 **正确**
    如果需要修改，请直接输入您的修改意见。
    """
    res = await cl.AskUserMessage(content=review_msg, timeout=300).send()
    # BUGFIX: 使用 'output' 键获取用户回复，而不是 'content'
    if res and res["output"].strip() == "正确":
        state["user_feedback"] = "正确"
    else:
        state["user_feedback"] = res["output"] if res else "用户未提供反馈。"

    return state


@cl.step(name="2. 查询数据库元数据")
async def query_database_node(state: GraphState):
    """
    根据表名查询数据库，获取表结构信息。
    """
    table_name = state["structured_intent"].table_name
    await cl.Message(
        content=f"参数确认无误，正在查询 `{table_name}` 表的元数据..."
    ).send()

    schema = mock_db_query(table_name)
    if schema:
        state["table_schema"] = schema
        # 使用Pandas和Chainlit展示表格
        df = pd.DataFrame(schema["columns"])
        await cl.Message(
            content=f"成功获取 **{table_name}** ({schema['description']}) 的元数据信息：",
            elements=[
                cl.Dataframe(name=f"schema_{table_name}", content=df, size="large")
            ],
        ).send()
    else:
        state["error_message"] = (
            f"未在数据库中找到名为 '{table_name}' 的表。请检查表名是否正确。"
        )

    return state


@cl.step(name="3. 生成数据引擎配置 (LLM)", type="llm")
async def generate_config_node(state: GraphState):
    """
    根据表结构和用户约束，生成数据生成引擎的JSON配置。
    """
    state["retry_count"] = 0
    state["error_message"] = None

    # 清晰地构建Prompt
    system_prompt = """
    你是一个数据生成配置专家。你的任务是根据用户需求和数据库表结构，为数据生成引擎创建一个详细的JSON配置文件。

    # 规则说明
    1.  **JSON结构**: 顶级键应为 `tableName` 和 `rules`。
    2.  **`rules` 字段**: 是一个数组，每个元素对应表中的一个字段。
    3.  **字段配置**: 每个字段配置对象必须包含 `fieldName` 和 `generator`。
    4.  **`generator`**: 定义了数据生成方式，它是一个包含 `type` 和 `params` 的对象。
        - `type`: 生成器类型 (e.g., 'increment', 'random_string', 'random_number', 'enum', 'datetime', 'expression')。
        - `params`: 生成器所需的参数 (e.g., `start`, `length`, `min`, `max`, `values`, `format`, `expr`)。
    5.  **字段关联**: 使用 `expression` 类型生成器可以引用其他字段的值，格式为 `f"{fieldName}"`。

    # 示例
    - **自增ID**: `{"fieldName": "id", "generator": {"type": "increment", "params": {"start": 1}}}`
    - **随机姓名**: `{"fieldName": "name", "generator": {"type": "random_string", "params": {"pattern": "[\u4e00-\u9fa5]{2,3}"}}}` (2到3个中文字符)
    - **关联字段**: `{"fieldName": "full_name", "generator": {"type": "expression", "params": {"expr": "f'{first_name}_{last_name}'"}}}`

    请严格遵循以上规则和用户的具体要求。
    """

    user_prompt = f"""
    # 用户需求
    - **表名**: {state['table_schema']['name']}
    - **字段约束**: {state['structured_intent'].constraints}
    - **生成行数**: {state['structured_intent'].num_rows}

    # 表结构
    {json.dumps(state['table_schema'], indent=2, ensure_ascii=False)}

    # 用户反馈 (如有)
    {state.get('user_feedback', '无')}

    请根据以上所有信息，生成最终的JSON配置文件。
    """

    while state["retry_count"] < MAX_RETRIES:
        try:
            # 使用 .ainvoke 而不是 with_structured_output 来获取原始JSON字符串，便于展示
            response = await llm.ainvoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            # 提取并解析JSON
            json_str = (
                response.content.strip().replace("```json", "").replace("```", "")
            )
            config_json = json.loads(json_str)
            state["generation_config_json"] = config_json
            state["user_feedback"] = None  # 清空反馈
            return state
        except Exception as e:
            state["retry_count"] += 1
            await cl.Message(
                content=f"配置生成失败，正在进行第 {state['retry_count']}/{MAX_RETRIES} 次重试... 错误: {e}"
            ).send()
            await asyncio.sleep(1)

    state["error_message"] = f"配置生成在重试{MAX_RETRIES}次后仍然失败。"
    return state


@cl.step(name="审查JSON配置")
async def config_review_node(state: GraphState):
    """
    中断流程，让人工审查生成的JSON配置。
    """
    if state.get("error_message"):
        return state

    config_json = state["generation_config_json"]
    pretty_json = json.dumps(config_json, indent=4, ensure_ascii=False)

    await cl.Message(
        content="系统已根据您的要求生成了以下数据生成引擎配置，请审查：",
        # BUGFIX: 直接使用导入的 Code 类
        elements=[
            Code(content=pretty_json, language="json", title="engine_config.json")
        ],
    ).send()

    review_msg = """
    如果配置正确，请输入 **生成** 以开始数据生成。
    如果需要修改，请直接输入您的修改意见。
    """
    res = await cl.AskUserMessage(content=review_msg, timeout=300).send()

    # BUGFIX: 使用 'output' 键获取用户回复，而不是 'content'
    if res and res["output"].strip() == "生成":
        state["user_feedback"] = "生成"
    else:
        state["user_feedback"] = res["output"] if res else "用户未提供反馈。"

    return state


@cl.step(name="4. 调用数据生成引擎")
async def post_to_engine_node(state: GraphState):
    """
    将配置POST到数据生成引擎，并获取结果。
    """
    config_json = state["generation_config_json"]
    result_url = await mock_data_engine_service(config_json)
    state["result_url"] = result_url
    return state


@cl.step(name="5. 展示结果")
async def show_result_node(state: GraphState):
    """
    在UI中展示最终的下载链接。
    """
    url = state["result_url"]
    await cl.Message(
        content=f"🎉 数据生成成功！\n\n您可以点击以下链接下载结果：\n[{url}]({url})"
    ).send()
    return state


@cl.step(name="处理错误")
async def error_node(state: GraphState):
    """
    处理流程中的错误，并向用户报告。
    """
    await cl.Message(
        content=f"❌ 流程中断，发生错误：\n\n`{state['error_message']}`"
    ).send()
    return state


# --- 5. LangGraph 条件边 ---


def should_continue_after_intent_review(state: GraphState):
    if state.get("error_message"):
        return "error"
    if state.get("user_feedback") == "正确":
        return "continue"
    return "revise_intent"


def should_continue_after_config_review(state: GraphState):
    if state.get("error_message"):
        return "error"
    if state.get("user_feedback") == "生成":
        return "continue"
    return "revise_config"


# --- 6. 构建LangGraph工作流 ---

workflow = StateGraph(GraphState)

# 添加节点
workflow.add_node("intent_recognition", intent_recognition_node)
workflow.add_node("intent_review", intent_review_node)
workflow.add_node("query_database", query_database_node)
workflow.add_node("generate_config", generate_config_node)
workflow.add_node("config_review", config_review_node)
workflow.add_node("post_to_engine", post_to_engine_node)
workflow.add_node("show_result", show_result_node)
workflow.add_node("error_handler", error_node)

# 设置入口点
workflow.set_entry_point("intent_recognition")

# 添加边
workflow.add_edge("intent_recognition", "intent_review")
workflow.add_edge("query_database", "generate_config")
workflow.add_edge("generate_config", "config_review")
workflow.add_edge("post_to_engine", "show_result")

# 添加条件边
workflow.add_conditional_edges(
    "intent_review",
    should_continue_after_intent_review,
    {
        "continue": "query_database",
        "revise_intent": "intent_recognition",
        "error": "error_handler",
    },
)

workflow.add_conditional_edges(
    "config_review",
    should_continue_after_config_review,
    {
        "continue": "post_to_engine",
        "revise_config": "generate_config",
        "error": "error_handler",
    },
)

# 连接到终点
workflow.add_edge("show_result", END)
workflow.add_edge("error_handler", END)

# 编译Graph
app = workflow.compile()


# --- 7. Chainlit UI交互 ---


@cl.on_chat_start
async def start_chat():
    cl.user_session.set("graph_runner", app)
    await cl.Message(
        content="您好！我是您的测试数据生成助手。\n\n"
        "请告诉我您想为什么表生成数据，以及具体的要求。\n\n"
        "**例如：**\n"
        "我想为 `users` 表生成100条用户数据，要求年龄在18到40岁之间，邮箱必须是gmail后缀。"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    graph_runner = cl.user_session.get("graph_runner")

    inputs = {"user_initial_intent": message.content}

    # ainvoke_stream 在这里可以实时显示每一步的状态
    async for output in graph_runner.astream(inputs, {"recursion_limit": 20}):
        # astream() returns states after each step is executed
        # We can inspect the state and display information to the user
        pass
