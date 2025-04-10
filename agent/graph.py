from typing import Dict, Any
from langgraph.graph import StateGraph
from .nodes import (
    analyze_metadata_node,
    generate_data_node,
    validate_data_node,
    should_regenerate
)

def create_workflow() -> StateGraph:
    """创建数据生成工作流图"""
    
    workflow = StateGraph()
    
    # 添加节点
    workflow.add_node("analyze_metadata", analyze_metadata_node)
    workflow.add_node("generate_data", generate_data_node)
    workflow.add_node("validate_data", validate_data_node)
    
    # 设置工作流程
    workflow.set_entry_point("analyze_metadata")
    workflow.add_edge("analyze_metadata", "generate_data")
    workflow.add_edge("generate_data", "validate_data")
    
    # 添加条件分支
    workflow.add_conditional_edges(
        "validate_data",
        should_regenerate,
        {
            True: "generate_data",  # 验证失败时重新生成
            False: "end"            # 验证通过时结束
        }
    )
    
    return workflow.compile()

async def run_workflow(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """运行数据生成工作流"""
    workflow = create_workflow()
    
    # 准备初始状态
    initial_state = {
        "metadata": metadata,
        "field_info": {},
        "validation_rules": {},
        "attempts": 0,
        "max_attempts": 3
    }
    
    # 执行工作流
    final_state = await workflow.ainvoke(initial_state)
    return final_state