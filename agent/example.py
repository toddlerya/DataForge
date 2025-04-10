import asyncio
from .graph import run_workflow

async def main():
    # 示例元数据
    metadata = {
        "table_name": "user_profile",
        "fields": [
            {
                "field_name": "customer_type",
                "data_type": "varchar(20)",
                "required": True,
                "zh_name": "客户类型",
                "category": "基础属性",
                "dict_type": "customer_type_dict",
                "comment": "区分个人客户和企业客户"
            }
        ]
    }
    
    # 运行工作流
    result = await run_workflow(metadata)
    print("生成结果:", result)

if __name__ == "__main__":
    asyncio.run(main())