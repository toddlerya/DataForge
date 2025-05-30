from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import random # Added for null_probability
from faker import Faker # Added for Faker Engine
import json # Added for JSON Outputter
from langgraph.graph import StateGraph, END # Added for LangGraph

# AppState related TypedDicts as defined in section 3.1
class TableFieldDefinition(TypedDict):
    """字段定义"""
    chinese_name: str
    english_name: str
    field_type: str
    sample_value: str
    constraints: List[str]

class FakerExecutionInstruction(TypedDict):
    """Faker 执行指令 (作为 AppState 的一部分，可能与 PydanticFakerInstruction 有重叠)
       根据文档3.1，这似乎是LLM生成计划后，在AppState中存储的一种形式。
       然而，文档3.2.3中定义了PydanticFakerInstruction作为LLM的输出结构。
       为了保持一致性并遵循Pydantic的最佳实践，LLM的输出将直接使用Pydantic模型。
       此TypedDict可能用于AppState内部表示，或在细化后与Pydantic版本统一。
       暂时按照文档3.1定义。
    """
    field_name: str
    faker_provider: str
    faker_parameters: Dict[str, Any]
    is_nullable: bool
    null_probability: float
    dependencies: List[str]
    custom_logic_description: str
    string_format_template: Optional[str]

class FakerExecutionPlan(TypedDict):
    """Faker 执行计划 (作为 AppState 的一部分)
       同上，这似乎是AppState中存储LLM计划的一种形式。
    """
    plan_description: str
    faker_locale: Optional[str]
    instructions_for_fields: List[FakerExecutionInstruction] # 使用上面定义的TypedDict

class AppState(TypedDict):
    """应用状态定义"""
    input_table_definitions: List[TableFieldDefinition]
    input_constraints_text: Optional[str]
    # LLM 生成的 Faker 执行计划将使用 PydanticFakerPlan
    llm_faker_plan: Optional['PydanticFakerPlan'] # 使用字符串避免前向引用问题
    generated_data_intermediate: List[Dict[str, Any]] # 文档为 List[List[Any]]，但Dict更常用
    generated_data_json: str
    error_message: Optional[str]
    num_rows_to_generate: int

# Pydantic models for LLM output as defined in section 3.2.3
class PydanticFakerInstruction(BaseModel):
    """LLM 输出的单个字段Faker指令 Pydantic模型"""
    field_name: str = Field(description="需要生成数据的字段的英文名称。")
    faker_provider: str = Field(description="要使用的 Python Faker provider 方法 (例如 'pyint', 'name', 'address', 'date_between')。如果无法直接映射，则使用 'custom_logic'。")
    faker_parameters: Dict[str, Any] = Field(default_factory=dict, description="传递给 Faker provider 方法的参数字典。例如：pyint 的 {'min_value': 0, 'max_value': 99}。对于 date_between，可使用 {'start_date': '-1y', 'end_date': 'today'}。")
    is_nullable: bool = Field(default=False, description="该字段是否可以为 null。如果为 True，还需考虑 null_probability。")
    null_probability: Optional[float] = Field(default=0.0, description="如果 is_nullable 为 True，则此字段生成 null 值的概率 (0.0 到 1.0)。")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="此字段生成所依赖的其他 field_name 列表 (用于复杂的字段间约束)。")
    custom_logic_description: Optional[str] = Field(default=None, description="如果 Faker 无法通过 provider 和参数直接处理，则需要自定义逻辑或验证的自然语言描述。例如：'确保值是质数'，或 '结束日期必须在开始日期字段之后'。")
    string_format_template: Optional[str] = Field(default=None, description="如果字段类型是字符串但需要特定格式 (例如 'ID-####')，请提供模板。使用 # 表示数字，? 表示字母。示例：'USER_??_####'。")

class PydanticFakerPlan(BaseModel):
    """LLM 输出的Faker执行计划 Pydantic模型"""
    plan_description: str = Field(default="使用 Python Faker 生成伪造数据的执行计划。", description="此计划的简要描述。")
    faker_locale: Optional[str] = Field(default=None, description="Faker 使用的区域设置，例如 'en_US', 'zh_CN'。如果可能，从输入上下文中确定。")
    instructions_for_fields: List[PydanticFakerInstruction] = Field(description="指令列表，表中的每个字段对应一个指令。")

# 为了 AppState 中的 llm_faker_plan 类型提示能正确解析
AppState.__annotations__['llm_faker_plan'] = Optional[PydanticFakerPlan]

# Placeholder for actual LLM and LangChain imports
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate

# Node 1: LLM Planner
def llm_planner_node(state: AppState) -> AppState:
    """节点1：LLM Planner - 解析Schema和约束，生成Faker执行计划。
    在此模拟实现中，我们将返回一个硬编码的计划。
    在实际应用中，这里会调用LLM并使用LangChain的with_structured_output。
    """
    print("--- LLM Planner Node --- ")
    table_definitions = state["input_table_definitions"]
    constraints_text = state.get("input_constraints_text", "") # Safely get optional text

    # --- 在此模拟LLM调用 --- 
    # 实际场景: 构建详细的prompt，包含表定义、约束、PydanticFakerPlan的schema等
    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", "You are an expert system... {pydantic_schema}"),
    #     ("human", "Table definitions: {table_defs}\nConstraints: {constraints}")
    # ])
    # llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    # structured_llm = llm.with_structured_output(PydanticFakerPlan)
    # chain = prompt | structured_llm
    # llm_faker_plan = chain.invoke({
    #     "pydantic_schema": PydanticFakerPlan.model_json_schema(),
    #     "table_defs": table_definitions,
    #     "constraints": constraints_text
    # })
    # --- 模拟结束 ---

    # 模拟LLM返回的计划 (基于方案中的表1示例)
    # 注意：这个模拟计划需要与 input_table_definitions 对应起来才有意义
    # 为了简单起见，我们假设 input_table_definitions 包含 user_id, username, age, email, reg_date, salary, department
    
    simulated_instructions = []
    for field_def in table_definitions:
        field_name = field_def['english_name']
        field_type = field_def['field_type']
        sample_value = field_def['sample_value']
        constraints = field_def['constraints']
        
        instruction = PydanticFakerInstruction(field_name=field_name, faker_provider="pystr", faker_parameters={})

        if field_name == "user_id":
            instruction.faker_provider = "pyint"
            instruction.faker_parameters = {"min_value": 1000, "max_value": 9999}
            instruction.is_nullable = False # 假设根据 "user_id IS NOT NULL"
        elif field_name == "username":
            instruction.faker_provider = "user_name"
            instruction.faker_parameters = {}
            instruction.is_nullable = False # 假设根据 "username IS NOT NULL"
        elif field_name == "age":
            instruction.faker_provider = "pyint"
            # 假设LLM解析了 "age > 18 AND age < 65"
            instruction.faker_parameters = {"min_value": 19, "max_value": 64} 
        elif field_name == "email":
            instruction.faker_provider = "email"
        elif field_name == "reg_date":
            instruction.faker_provider = "date_between"
            # 假设LLM解析了 'reg_date > "2022-01-01"'
            instruction.faker_parameters = {"start_date": "-2y", "end_date": "today"} # 简化模拟
        elif field_name == "salary":
            instruction.faker_provider = "pydecimal"
            instruction.faker_parameters = {"left_digits": 5, "right_digits": 2, "positive": True, "min_value": 1000, "max_value": 99999}
            # 假设LLM解析了 "salary < 100000.00"
        elif field_name == "department":
            instruction.faker_provider = "random_element"
            # 假设LLM解析了 "department IN ('Sales', 'IT', 'HR')"
            instruction.faker_parameters = {"elements": ['Sales', 'IT', 'HR']}
        else:
            # 默认或基于类型的简单映射
            if field_type == "INT":
                instruction.faker_provider = "pyint"
            elif field_type == "VARCHAR":
                instruction.faker_provider = "word"
            elif field_type == "DATE":
                instruction.faker_provider = "date_object"
            elif field_type == "BOOLEAN":
                instruction.faker_provider = "pybool"
            elif field_type == "DECIMAL":
                instruction.faker_provider = "pyfloat"
        
        # 简单处理 IS NOT NULL
        if any("IS NOT NULL" in c.upper() for c in constraints):
            instruction.is_nullable = False

        simulated_instructions.append(instruction)

    llm_faker_plan = PydanticFakerPlan(
        plan_description="Simulated Faker execution plan based on input table definitions.",
        faker_locale="zh_CN", # 假设从上下文中推断
        instructions_for_fields=simulated_instructions
    )

    print(f"  Generated Faker Plan: {llm_faker_plan.model_dump_json(indent=2)}")

    # 更新状态
    state["llm_faker_plan"] = llm_faker_plan
    state["error_message"] = None # 清除之前的错误（如果有）
    return state

# Node 2: Faker Engine
def faker_engine_node(state: AppState) -> AppState:
    """节点2：Faker Engine - 根据计划生成数据。"""
    print("--- Faker Engine Node --- ")
    llm_plan = state.get("llm_faker_plan")
    num_rows = state.get("num_rows_to_generate", 1) # Default to 1 if not specified

    if not llm_plan:
        state["error_message"] = "Faker Engine Error: LLM Faker plan is missing."
        print(f"  Error: {state['error_message']}")
        # Potentially, we could return state here or raise an exception
        # For LangGraph, updating state with error and returning is common
        return state

    generated_rows: List[Dict[str, Any]] = []
    
    # Initialize Faker instance
    # Use locale from plan if available, otherwise Faker defaults (usually en_US)
    fake = Faker(locale=llm_plan.faker_locale if llm_plan.faker_locale else None)
    
    # Seed for reproducibility if needed (can be passed in AppState or configured globally)
    # Faker.seed(0) # Or fake.seed_instance(0)

    for i in range(num_rows):
        current_row: Dict[str, Any] = {}
        print(f"  Generating row {i+1}/{num_rows}")
        for instruction in llm_plan.instructions_for_fields:
            field_name = instruction.field_name
            value: Any = None # Default value

            # 1. Handle nullability
            if instruction.is_nullable and instruction.null_probability is not None:
                if random.random() < instruction.null_probability:
                    current_row[field_name] = None
                    print(f"    Field '{field_name}': null (due to probability)")
                    continue # Move to next instruction for this row
            
            # 2. Handle custom_logic_description (placeholder for now)
            # In a real system, this might trigger specific Python functions or further LLM calls.
            if instruction.faker_provider == "custom_logic":
                # For simulation, we'll use a placeholder value or log it.
                # A more advanced system might try to interpret custom_logic_description
                # or have a registry of custom functions.
                value = f"CUSTOM_LOGIC_FOR_{field_name}: {instruction.custom_logic_description or 'Not specified'}"
                print(f"    Field '{field_name}': '{value}' (custom logic placeholder)")
                current_row[field_name] = value
                continue

            # 3. Get and call Faker provider method
            try:
                provider_method = getattr(fake, instruction.faker_provider)
                # Ensure faker_parameters is a dict, even if empty from Pydantic default_factory
                params = instruction.faker_parameters if instruction.faker_parameters is not None else {}
                value = provider_method(**params)
                print(f"    Field '{field_name}': provider '{instruction.faker_provider}', params {params}, raw_value '{value}'")

                # 4. Handle string_format_template if provided and value is a string
                # This is a simplified approach. A more robust one would check if the provider
                # itself can handle formatting, or if the template is for numbers etc.
                if instruction.string_format_template and isinstance(value, str):
                    # This is a very basic interpretation. Faker's bothify/regexify are more powerful.
                    # LLM should ideally suggest 'bothify' or 'regexify' as provider with the template as a parameter.
                    # For now, let's assume the template is simple and we just prepend/append or use it directly if value is placeholder.
                    # A better simulation for string_format_template would be to use fake.bothify if the LLM planned it.
                    # If the provider was 'bothify', params would include 'text': instruction.string_format_template
                    # This part needs refinement based on how LLM is prompted to use string_format_template.
                    # For now, if template exists, we assume it's a format string for the generated value or a direct template.
                    try:
                        # Attempt to format if value is not a placeholder from custom_logic
                        if f"CUSTOM_LOGIC_FOR_{field_name}" not in str(value):
                             # This is a naive formatting, real use might involve more complex templating
                            formatted_value = instruction.string_format_template.replace("#", str(random.randint(0,9))).replace("?", random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")) 
                            # This is not using the 'value' from provider if template is present, which might be wrong.
                            # Let's assume if template is present, it's a direct command for 'bothify' or similar.
                            # The LLM should ideally set faker_provider to 'bothify' and pass the template in faker_parameters.
                            # Re-evaluating: if string_format_template is present, it should have been handled by LLM
                            # setting provider to 'bothify' or 'regexify'. If not, this is a fallback or misinterpretation.
                            # For this simulation, let's assume if template is there, we use it with bothify.
                            value = fake.bothify(text=instruction.string_format_template)
                            print(f"      Formatted value (bothify with template): '{value}'")
                    except Exception as e:
                        print(f"      Error applying string_format_template for {field_name}: {e}")
                        # Fallback to original value if formatting fails
            
            except AttributeError:
                error_msg = f"Faker Engine Error: Provider '{instruction.faker_provider}' not found for field '{field_name}'."
                print(f"    Error: {error_msg}")
                state["error_message"] = error_msg
                # Decide: stop all generation, or fill with placeholder and continue?
                # For now, fill with error placeholder and continue with other fields/rows.
                value = f"ERROR_PROVIDER_NOT_FOUND: {instruction.faker_provider}"
            except Exception as e:
                error_msg = f"Faker Engine Error: Failed to generate data for field '{field_name}' using provider '{instruction.faker_provider}' with params {instruction.faker_parameters}. Error: {e}"
                print(f"    Error: {error_msg}")
                state["error_message"] = error_msg # Store last error
                value = f"ERROR_GENERATING_DATA: {e}"
            
            current_row[field_name] = value
        generated_rows.append(current_row)
        print(f"  Generated row data: {current_row}")

    state["generated_data_intermediate"] = generated_rows
    if not state.get("error_message"):
         print(f"  Successfully generated {len(generated_rows)} rows.")
    return state

# Node 3: JSON Outputter
def json_output_node(state: AppState) -> AppState:
    """节点3：JSON Outputter - 将生成的数据转换为JSON字符串。"""
    print("--- JSON Outputter Node --- ")
    intermediate_data = state.get("generated_data_intermediate")

    if intermediate_data is None:
        error_msg = "JSON Outputter Error: Intermediate data is missing."
        state["error_message"] = error_msg
        print(f"  Error: {error_msg}")
        state["generated_data_json"] = "[]" # Output empty JSON array on error
        return state
    
    try:
        # ensure_ascii=False to correctly handle non-ASCII characters like Chinese names
        json_output = json.dumps(intermediate_data, indent=2, ensure_ascii=False)
        state["generated_data_json"] = json_output
        print(f"  Successfully converted intermediate data to JSON string.")
        # print(f"  JSON Output: \n{json_output[:500]}...") # Print a snippet
    except TypeError as e:
        error_msg = f"JSON Outputter Error: Failed to serialize data to JSON. Error: {e}"
        state["error_message"] = error_msg
        print(f"  Error: {error_msg}")
        state["generated_data_json"] = "[]" # Output empty JSON array on error
    
    return state

# LangGraph Workflow Definition
workflow = StateGraph(AppState)

# Add nodes to the graph
workflow.add_node("llm_planner", llm_planner_node)
workflow.add_node("faker_engine", faker_engine_node)
workflow.add_node("json_outputter", json_output_node)

# Define the edges for the workflow
workflow.add_edge("llm_planner", "faker_engine")
workflow.add_edge("faker_engine", "json_outputter")
workflow.add_edge("json_outputter", END)

# Set the entry point for the graph
workflow.set_entry_point("llm_planner")

# Compile the graph
app = workflow.compile()

if __name__ == '__main__':
    # 示例用法 (可选，用于基本测试)
    sample_field_def = TableFieldDefinition(
        chinese_name="用户ID",
        english_name="user_id",
        field_type="INT",
        sample_value="1001",
        constraints=["user_id IS NOT NULL", "UNIQUE"]
    )

    sample_instruction_pydantic = PydanticFakerInstruction(
        field_name="age",
        faker_provider="pyint",
        faker_parameters={"min_value": 18, "max_value": 65},
        is_nullable=False
    )

    sample_plan_pydantic = PydanticFakerPlan(
        plan_description="生成用户信息的计划",
        faker_locale="zh_CN",
        instructions_for_fields=[sample_instruction_pydantic]
    )

    initial_state = AppState(
        input_table_definitions=[sample_field_def],
        input_constraints_text="age > 18 AND age < 65",
        llm_faker_plan=None, # 初始为空，由LLM Planner填充
        generated_data_intermediate=[],
        generated_data_json="",
        error_message=None,
        num_rows_to_generate=10
    )

    print("Sample TableFieldDefinition:", sample_field_def)
    print("Sample PydanticFakerInstruction:", sample_instruction_pydantic.model_dump_json(indent=2))
    print("Sample PydanticFakerPlan:", sample_plan_pydantic.model_dump_json(indent=2))
    print("Initial AppState:", initial_state)

    # --- Test LLM Planner Node ---
    # 准备一个更完整的 initial_state 用于测试 llm_planner_node
    sample_table_defs_for_planner = [
        TableFieldDefinition(chinese_name="用户ID", english_name="user_id", field_type="INT", sample_value="1001", constraints=["user_id IS NOT NULL", "UNIQUE"]),
        TableFieldDefinition(chinese_name="用户名", english_name="username", field_type="VARCHAR(50)", sample_value="zhang_san", constraints=["username IS NOT NULL"]),
        TableFieldDefinition(chinese_name="年龄", english_name="age", field_type="INT", sample_value="25", constraints=["age > 18", "age < 65"]),
        TableFieldDefinition(chinese_name="邮箱", english_name="email", field_type="VARCHAR(100)", sample_value="test@example.com", constraints=["email IS VALID EMAIL"]),
        TableFieldDefinition(chinese_name="注册日期", english_name="reg_date", field_type="DATE", sample_value="2023-01-15", constraints=["reg_date > '2022-01-01'"]),
        TableFieldDefinition(chinese_name="薪水", english_name="salary", field_type="DECIMAL(10,2)", sample_value="8000.50", constraints=["salary < 100000.00"]),
        TableFieldDefinition(chinese_name="部门", english_name="department", field_type="VARCHAR(20)", sample_value="Sales", constraints=["department IN ('Sales', 'IT', 'HR')"])
    ]
    planner_test_state = AppState(
        input_table_definitions=sample_table_defs_for_planner,
        input_constraints_text="Global constraint: All users must be active (simulated)",
        llm_faker_plan=None,
        generated_data_intermediate=[],
        generated_data_json="",
        error_message=None,
        num_rows_to_generate=5
    )
    print("\n--- Testing LLM Planner Node ---")
    updated_state_after_planner = llm_planner_node(planner_test_state)
    print(f"State after LLM Planner: {updated_state_after_planner}")

    # --- Test Faker Engine Node ---
    if updated_state_after_planner.get("llm_faker_plan"):
        print("\n--- Testing Faker Engine Node ---")
        state_after_faker = faker_engine_node(updated_state_after_planner)
        print(f"State after Faker Engine (first 5 rows of {len(state_after_faker.get('generated_data_intermediate', []))} generated):")
        for i, row in enumerate(state_after_faker.get("generated_data_intermediate", [])[:5]):
            print(f"  Row {i+1}: {row}")
        if state_after_faker.get("error_message"):
            print(f"  Faker Engine Error: {state_after_faker['error_message']}")
    else:
        print("\nSkipping Faker Engine test as LLM plan was not generated.")

    # --- Test JSON Outputter Node (can be tested similarly if needed, but graph will test it) ---

    # --- Test the full LangGraph App ---
    print("\n--- Testing Full LangGraph App ---")
    # Use the same planner_test_state or a new initial state
    initial_app_state_input = {
        "input_table_definitions": sample_table_defs_for_planner, # Defined in previous test
        "input_constraints_text": "Global constraint: All users must be active (simulated)",
        "num_rows_to_generate": 3 # Let's generate 3 rows for the full app test
        # llm_faker_plan, generated_data_intermediate, generated_data_json, error_message will be populated by the graph
    }

    # Invoke the compiled graph
    # The stream() method returns an iterator of all intermediate states.
    # The final state is the last one.
    final_state = None
    for s in app.stream(initial_app_state_input):
        # s is a dictionary where keys are node names and values are the AppState after that node ran
        print(f"\nState after node {list(s.keys())[0]}:")
        # print(json.dumps(list(s.values())[0], indent=2, ensure_ascii=False, default=str)) # Print full state
        current_step_output = list(s.values())[0]
        if 'llm_faker_plan' in current_step_output and current_step_output['llm_faker_plan']:
            print(f"  LLM Plan: {'Generated' if current_step_output['llm_faker_plan'] else 'Not yet'}")
        if 'generated_data_intermediate' in current_step_output and current_step_output['generated_data_intermediate']:
            print(f"  Intermediate Data: {len(current_step_output['generated_data_intermediate'])} rows generated")
        if 'generated_data_json' in current_step_output and current_step_output['generated_data_json']:
            print(f"  JSON Output: Generated (length {len(current_step_output['generated_data_json'])})")
        if 'error_message' in current_step_output and current_step_output['error_message']:
            print(f"  Error: {current_step_output['error_message']}")
        final_state = current_step_output
    
    print("\n--- Final Output from LangGraph App ---")
    if final_state and final_state.get("generated_data_json"):
        print("Generated JSON Data:")
        print(final_state["generated_data_json"])
    elif final_state and final_state.get("error_message"):
        print(f"Error in final state: {final_state['error_message']}")
    else:
        print("No JSON data generated or an unknown error occurred.")