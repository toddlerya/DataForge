from typing import Dict, Any
from .agents import MetadataAnalysisAgent, DataGenerationAgent, DataValidationAgent

async def analyze_metadata_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """元数据分析节点"""
    agent = MetadataAnalysisAgent()
    analysis_result = await agent.analyze_metadata(state["metadata"])
    return {**state, "metadata_analysis": analysis_result}

async def generate_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """数据生成节点"""
    agent = DataGenerationAgent()
    generated_data = await agent.generate_data(state["field_info"])
    return {**state, "generated_data": generated_data}

async def validate_data_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """数据验证节点"""
    agent = DataValidationAgent()
    validation_result = await agent.validate_data(
        state["generated_data"],
        state["validation_rules"]
    )
    return {**state, "validation_result": validation_result}

def should_regenerate(state: Dict[str, Any]) -> bool:
    """判断是否需要重新生成数据"""
    return not state.get("validation_result", {}).get("is_valid", False)