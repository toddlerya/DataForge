from typing import Dict, List, Optional
from langgraph.graph import StateGraph, Graph
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

class MetadataAnalysisAgent:
    """元数据分析Agent，负责解析和理解数据仓库元数据"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(temperature=0)
        self.system_prompt = """你是一个专业的数据仓库元数据分析专家。
你的任务是分析数据表的元数据信息，理解表结构、字段含义和业务规则。"""
    
    async def analyze_metadata(self, metadata: Dict) -> Dict:
        """分析元数据信息"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "请分析以下元数据信息:\n{metadata}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"metadata": str(metadata)})
        return {"analysis": response.content}

class DataGenerationAgent:
    """数据生成Agent，负责生成符合规则的仿真数据"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(temperature=0.7)
        self.system_prompt = """你是一个专业的数据生成专家。
你的任务是根据数据表的元数据定义和业务规则生成符合要求的仿真数据。"""
    
    async def generate_data(self, field_info: Dict) -> Dict:
        """生成单个字段的数据"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """请为以下字段生成符合要求的数据:
字段名称: {field_name}
数据类型: {data_type}
业务规则: {business_rules}""")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke(field_info)
        return {"generated_data": response.content}

class DataValidationAgent:
    """数据验证Agent，负责验证生成数据的质量和一致性"""
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(temperature=0)
        self.system_prompt = """你是一个专业的数据质量验证专家。
你的任务是验证生成数据是否符合业务规则和数据一致性要求。"""
    
    async def validate_data(self, data: Dict, rules: Dict) -> Dict:
        """验证数据质量"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """请验证以下数据是否符合规则:
数据: {data}
规则: {rules}""")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"data": str(data), "rules": str(rules)})
        return {"validation_result": response.content}