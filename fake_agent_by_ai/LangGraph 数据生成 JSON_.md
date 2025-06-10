# **利用 LangGraph 与 Faker 实现基于 LLM 的智能化测试数据生成**

## **摘要**

在软件开发与测试生命周期中，高质量的测试数据对于确保应用质量至关重要。传统手动创建或简单脚本生成数据的方式，在面对复杂数据结构、多样化约束条件以及大规模数据需求时，往往效率低下且难以满足真实场景的模拟。本文提出了一种基于大型语言模型（LLM）、LangGraph 框架以及 Python Faker 库的智能化测试数据生成方案。该方案利用 LLM 解析表结构定义和约束条件，生成 Faker 执行计划；通过 LangGraph 构建可控、可扩展的数据生成流程；并借助 Faker 库强大的数据模拟能力，最终输出符合要求的 JSON 格式测试数据。本文将详细阐述该方案的核心技术、系统架构、关键节点设计、实现细节以及高级应用策略。

## **1\. 引言**

随着信息技术的飞速发展，软件系统的复杂性日益增加，对测试的深度和广度也提出了更高要求。测试数据作为验证软件功能、性能和稳定性的基石，其质量直接影响测试效果。然而，获取和构造满足特定业务规则、数据类型及约束条件的测试数据，尤其是在涉及隐私保护、数据多样性及大规模数据集的场景下，是一项充满挑战的任务。

大型语言模型（LLM）凭借其强大的自然语言理解和生成能力，为自动化解析数据需求和生成执行逻辑提供了新的可能性 1。LangGraph 作为一个用于构建基于 LLM 的有状态、多步骤应用的框架，通过其图结构定义工作流，使得复杂应用逻辑的编排更为清晰和可控 3。Python Faker 库则是一个功能丰富的工具，能够生成各种类型的伪造数据，从简单的姓名、地址到复杂的金融信息等，并支持本地化和自定义扩展 5。

本文旨在结合 LLM 的智能规划、LangGraph 的流程编排以及 Faker 的数据生成能力，构建一个自动化的仿真测试数据生成系统。该系统能够接收用户提供的表结构定义（包括字段中文名、英文名、字段类型、字段样例值）以及字段间的约束条件（如 a\_field is not null, b\_field \< 100），并最终以 JSON 格式输出符合要求的仿真测试数据。

## **2\. 核心技术概览**

构建本方案依赖于对以下几项核心技术的理解和应用：

### **2.1. LangGraph：构建有状态的多智能体应用**

LangGraph 是一个用于构建基于图的工作流应用的框架，特别适用于需要管理状态、具有循环和条件分支的复杂 LLM 应用 4。其核心概念包括：

* **状态（State）**: 一个共享的数据结构，通常是 Python 的 TypedDict 或 Pydantic BaseModel，代表了应用的当前快照。状态在图的节点间传递和更新 9。
* **节点（Nodes）**: Python 函数，封装了应用的逻辑单元。节点接收当前状态作为输入，执行计算或副作用，并返回更新后的状态 8。节点可以执行调用 LLM、数据处理、API 访问等多种任务 10。
* **边（Edges）**: 定义节点之间的连接和流程。边可以是固定的，也可以是基于当前状态进行条件判断的，从而决定下一个执行哪个节点 8。
* **图（Graph）**: 由节点和边组成的结构，定义了应用的整体执行流程。StateGraph 是 LangGraph 中常用的图类型 4。图的执行通常从一个入口点（Entry Point）开始，直到达到一个特殊的 END 节点 8。

LangGraph 通过这些组件，允许开发者构建可控、可靠且可扩展的智能体系统，支持长时运行工作流、人机协作以及实时流式处理 3。

### **2.2. Python Faker：生成多样化的仿真数据**

Faker 是一个 Python 库，用于生成伪造数据，广泛应用于测试、原型设计、数据库填充等场景 5。其主要特性包括：

* **多样化的数据提供者（Providers）**: Faker 内置了大量的数据提供者，可以生成姓名、地址、电子邮件、文本、日期时间、银行信息、IP 地址等多种类型的数据 5。faker.providers.python 模块还提供了生成特定 Python 类型数据（如整数、浮点数、布尔值、字符串）的方法，并支持一些基本约束（如最大最小值、长度）14。
* **本地化支持**: Faker 支持多种语言环境，可以生成符合特定地区文化习惯的数据 5。
* **可扩展性**: 用户可以创建自定义的数据提供者（Custom Providers）以满足特定的数据生成需求 6。这对于实现复杂的数据格式或依赖关系至关重要。
* **可复现性**: 通过设置种子（Seed），Faker 可以生成可复现的数据集，这对于调试和回归测试非常有用 5。

### **2.3. 大型语言模型（LLM）：理解与规划**

LLM 在本方案中扮演核心的“大脑”角色，负责理解用户提供的表结构定义和自然语言描述的约束条件，并将其转化为结构化的、可供 Faker 使用的执行计划 2。关键在于：

* **提示工程（Prompt Engineering）**: 精心设计的提示是引导 LLM 正确理解任务并生成期望输出的关键 1。提示需要清晰地定义 LLM 的角色、输入格式、期望的输出结构以及处理各种约束的规则 18。
* **结构化输出（Structured Output）**: 为了确保 LLM 的输出能够被后续程序稳定解析和使用，要求 LLM 以特定格式（如 JSON）输出。LangChain 提供的 with\_structured\_output 功能，结合 Pydantic 模型，能够有效地将 LLM 的响应约束为预定义的 Python 对象结构 19。这对于生成 Faker 执行计划至关重要，因为计划本身需要是结构化的。LLM 需要有能力理解并遵循预定义的 schema，以确保输出的有效性 23。

## **3\. 系统架构与设计**

本节将详细描述基于 LangGraph 的测试数据生成系统的架构设计，包括状态定义、核心节点功能以及图的构建。

### **3.1. 应用状态定义 (AppState)**

在 LangGraph 中，状态对象在整个工作流程中传递和修改，承载着所有节点间共享的数据 8。一个精心设计的状态对象能够清晰地界定各节点间的输入输出，提高代码的可读性和可维护性，并为调试提供便利。对于本应用，我们定义 AppState 如下（使用 TypedDict）：

```python
from typing import TypedDict, List, Dict, Any, Optional

class TableFieldDefinition(TypedDict):
    \# 字段中文名
    chinese\_name: str
    \# 字段英文名
    english\_name: str
    \# 字段类型, e.g., "INT", "VARCHAR", "DATE", "BOOLEAN"
    field\_type: str
    \# 字段样例值
    sample\_value: str
    \# 字段约束条件列表, e.g., \["age \> 18", "name is not null"\]
    constraints: List\[str\]

class FakerExecutionInstruction(TypedDict):
    \# 字段英文名
    field\_name: str
    \# Faker provider 名称, e.g., "pyint", "name", "custom\_logic"
    faker\_provider: str
    \# Faker provider 参数, e.g., {"min\_value": 0, "max\_value": 99}
    faker\_parameters: Dict\[str, Any\]
    \# 是否可为空
    is\_nullable: bool
    \# 若可为空，为空的概率
    null\_probability: float
    \# 依赖的其他字段列表 (用于处理字段间依赖)
    dependencies: List\[str\]
    \# 若LLM无法直接映射，自定义逻辑的描述
    custom\_logic\_description: str
    \# 字符串格式化模板 (可选)
    string\_format\_template: Optional\[str\]

class FakerExecutionPlan(TypedDict):
    \# Faker 执行计划的描述
    plan\_description: str
    \# Faker 使用的区域设置 (可选)
    faker\_locale: Optional\[str\]
    \# 针对各字段的指令列表
    instructions\_for\_fields: List\[FakerExecutionInstruction\]

class AppState(TypedDict):
    \# 输入的表结构定义
    input\_table\_definitions: List
    \# 输入的全局约束文本 (如果全局提供)
    input\_constraints\_text: Optional\[str\]
    \# LLM 生成的 Faker 执行计划
    llm\_faker\_plan: Optional\[FakerExecutionPlan\]
    \# 中间生成的列表数据 (用于多行生成)
    generated\_data\_intermediate: List\]
    \# 最终生成的 JSON 字符串
    generated\_data\_json: str
    \# 错误信息 (用于错误处理)
    error\_message: Optional\[str\]
    \# 需要生成的行数
    num\_rows\_to\_generate: int
```

此 AppState 定义了从初始输入（表结构、约束、生成行数）到中间产物（LLM 的执行计划、Python 字典列表形式的生成数据）再到最终输出（JSON 字符串）以及可能的错误信息的所有数据。这种明确的状态管理方式，使得数据在 LLM Planner、Faker Engine 和 JSON Outputter 等节点间的流转清晰可见。

### **3.2. 节点 1：LLM Planner \- 解析 Schema 和约束**

此节点是系统的智能核心，负责将用户输入的表结构定义和约束条件转化为 Faker 库可以执行的结构化计划。

#### **3.2.1. 输入分析：表结构与约束语言**

LLM Planner 节点接收 AppState 中的 input\_table\_definitions（表结构定义列表）和可选的 input\_constraints\_text（全局约束字符串）。对于每个字段定义，LLM 需要综合考虑其中文名、英文名、字段类型、样例值以及附加的约束条件。

**表 1：输入表结构定义示例**

| 字段中文名 | 英文名 | 字段类型 | 字段样例值 | 约束条件 |
| :---- | :---- | :---- | :---- | :---- |
| 用户ID | user\_id | INT | 1001 | user\_id IS NOT NULL, UNIQUE |
| 用户名 | username | VARCHAR(50) | "zhang\_san" | username IS NOT NULL |
| 年龄 | age | INT | 25 | age \> 18 AND age \< 65 |
| 邮箱 | email | VARCHAR(100) | "test@example.com" | email IS VALID EMAIL |
| 注册日期 | reg\_date | DATE | "2023-01-15" | reg\_date \> "2022-01-01" |
| 薪水 | salary | DECIMAL(10,2) | 8000.50 | salary \< 100000.00 |
| 部门 | department | VARCHAR(20) | "Sales" | department IN ('Sales', 'IT', 'HR') |

这张表格清晰地展示了 LLM 需要处理的输入信息的多样性，为后续的提示工程提供了具体的上下文。

#### **3.2.2. 提示工程：实现理解与规划**

为 LLM Planner 设计一个详尽的提示至关重要。该提示应包含以下要素：

* **角色定义**: 明确告知 LLM 其扮演的角色，例如：“你是一个专家系统，负责将表结构定义和约束条件翻译成 Python Faker 库的执行计划。”
* **输出格式定义**: 提供目标输出 PydanticFakerPlan 和 PydanticFakerInstruction 的 Pydantic schema (或其 JSON 表示形式)。这是确保 LLM 生成结构化输出的关键 19。
* **字段解释**: 解释输出 schema 中每个字段的含义，例如 faker\_provider 应选择哪个 Faker 方法，faker\_parameters 如何构造，is\_nullable 的作用等。
* **映射指导**:
  * 指示 LLM 利用输入中的 field\_type (字段类型) 和 sample\_value (样例值) 作为选择 faker\_provider 的重要线索。
  * 提供常见约束条件到 faker\_parameters 或 PydanticFakerInstruction 其他字段的映射示例（例如，\> X 对应 {"min\_value": X+1}，IS NOT NULL 对应 is\_nullable=False）。
  * 指导 LLM 如何处理不同的数据类型：例如，"INT" 映射到 pyint，"VARCHAR" 映射到 pystr 或 text，"DATE" 映射到 date\_object 或特定格式的日期字符串，"BOOLEAN" 映射到 pybool，"DECIMAL" 映射到 pydecimal 或 pyfloat。
  * 对于无法直接映射或过于复杂的约束，指示 LLM 填充 custom\_logic\_description 字段。
  * 考虑基于输入上下文（如中文字段名）推断并设置 faker\_locale。
* **示例学习 (Few-Shot Learning)**: 提供少量高质量的输入-输出对示例，帮助 LLM 更好地理解任务并泛化到新的输入 1。

提示的设计应遵循清晰、具体、提供上下文、分解复杂任务等最佳实践 17。目标是让 LLM 能够准确地将自然语言和半结构化的输入转换为严格定义的、机器可读的 Faker 执行计划，确保 schema 依从性 23。LangChain 的 with\_structured\_output 功能与 Pydantic 模型的结合，是实现这一目标的首选方法 19。

提示的质量直接决定了 LLM 生成计划的准确性，进而影响最终生成数据的质量。因此，对提示进行迭代优化是必不可少的环节。一个清晰、全面的提示，如同为 LLM 提供了一份详细的任务说明书和微型教程，使其能够更好地完成从解析、解释到映射和结构化的复杂任务。

#### **3.2.3. 定义 "Faker 执行计划"：LLM 输出的 Pydantic Schema**

为了使 LLM 的输出能够被后续节点稳定地使用，我们采用 Pydantic 模型来严格定义 "Faker 执行计划" 的结构。这不仅为 LLM 提供了明确的输出目标，也为 LangChain 的 with\_structured\_output 功能提供了 schema 依据。

Python

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PydanticFakerInstruction(BaseModel):
    field\_name: str \= Field(description="需要生成数据的字段的英文名称。")
    faker\_provider: str \= Field(description="要使用的 Python Faker provider 方法 (例如 'pyint', 'name', 'address', 'date\_between')。如果无法直接映射，则使用 'custom\_logic'。")
    faker\_parameters: Dict\[str, Any\] \= Field(default\_factory=dict, description="传递给 Faker provider 方法的参数字典。例如：pyint 的 {'min\_value': 0, 'max\_value': 99}。对于 date\_between，可使用 {'start\_date': '-1y', 'end\_date': 'today'}。")
    is\_nullable: bool \= Field(default=False, description="该字段是否可以为 null。如果为 True，还需考虑 null\_probability。")
    null\_probability: Optional\[float\] \= Field(default=0.0, description="如果 is\_nullable 为 True，则此字段生成 null 值的概率 (0.0 到 1.0)。")
    dependencies: Optional\[List\[str\]\] \= Field(default\_factory=list, description="此字段生成所依赖的其他 field\_name 列表 (用于复杂的字段间约束)。")
    custom\_logic\_description: Optional\[str\] \= Field(default=None, description="如果 Faker 无法通过 provider 和参数直接处理，则需要自定义逻辑或验证的自然语言描述。例如：'确保值是质数'，或 '结束日期必须在开始日期字段之后'。")
    string\_format\_template: Optional\[str\] \= Field(default=None, description="如果字段类型是字符串但需要特定格式 (例如 'ID-\#\#\#\#')，请提供模板。使用 \# 表示数字，? 表示字母。示例：'USER\_??\_\#\#\#\#'。")

class PydanticFakerPlan(BaseModel):
    plan\_description: str \= Field(default="使用 Python Faker 生成伪造数据的执行计划。", description="此计划的简要描述。")
    faker\_locale: Optional\[str\] \= Field(default=None, description="Faker 使用的区域设置，例如 'en\_US', 'zh\_CN'。如果可能，从输入上下文中确定。")
    instructions\_for\_fields: List\[PydanticFakerInstruction\] \= Field(description="指令列表，表中的每个字段对应一个指令。")

这个 Pydantic schema 是 LLM Planner 节点输出的蓝图，也是其与 Faker Engine 节点之间的契约。field\_name、faker\_provider 和 faker\_parameters 构成了执行 Faker 方法的核心指令。is\_nullable 和 null\_probability 控制了空值的生成。dependencies 和 custom\_logic\_description 字段的设计尤为关键，它们允许 LLM 表达那些无法直接通过参数配置解决的复杂约束或字段间依赖关系，从而将这部分逻辑的处理“外包”给 Faker Engine 节点中的 Python 代码。string\_format\_template 字段则为 LLM 提供了一种规划 Faker bothify 或 regexify 功能的方式，以满足特定的字符串格式要求。这种设计在 LLM 的规划能力和 Faker Engine 的执行能力之间取得了平衡，使得系统更具鲁棒性和扩展性。

### **3.3. 节点 2：Faker Engine \- 根据计划生成数据**

此节点是实际的数据生成单元，它接收 LLM Planner 输出的 PydanticFakerPlan，并据此调用 Faker 库生成指定数量的数据行。

#### **3.3.1. 消费 LLM 的执行计划**

Faker Engine 节点从应用状态 AppState 中获取 llm\_faker\_plan 和 num\_rows\_to\_generate。它将循环 num\_rows\_to\_generate 次，在每次迭代中，遍历 plan.instructions\_for\_fields 列表，为表中的每个字段生成一个值，从而构成一行数据。

#### **3.3.2. 将计划映射到 Faker：调用 Provider 和应用参数**

对于计划中的每一条 PydanticFakerInstruction：

1. **初始化 Faker**: fake \= Faker(locale=plan.faker\_locale if plan.faker\_locale else None)。如果计划中指定了区域设置，则使用该设置初始化 Faker 实例。
2. **处理空值**: 如果 instruction.is\_nullable 为 True，则根据 instruction.null\_probability（例如，random.random() \< instruction.null\_probability）决定当前字段值是否为 None。若是，则跳过后续的 Faker 调用，直接将该字段值设为 None。
3. **获取 Faker Provider 方法**: 如果值不为 None，则通过 method\_to\_call \= getattr(fake, instruction.faker\_provider) 动态获取 Faker 实例上对应的 Provider 方法。
4. **调用方法并传递参数**: value \= method\_to\_call(\*\*instruction.faker\_parameters)。将指令中定义的参数解包后传递给获取到的 Faker 方法。
5. **处理字符串格式化模板**: 如果 instruction.string\_format\_template 被提供，则使用 fake.bothify(text=instruction.string\_format\_template) 或 fake.regexify(pattern=...) 来生成符合特定模式的字符串 13。LLM 的计划应指明使用哪种方法或提供相应的模板/正则表达式。
6. **存储生成的值**: 将生成的 value 存储起来，与 instruction.field\_name 关联，作为当前行数据的一部分。

为了保证数据生成的可复现性（如果需要），可以在 Faker Engine 的开始处或针对每个 Faker 实例使用 Faker.seed(some\_seed) 或 fake.seed\_instance(some\_seed) 进行播种 5。种子值可以作为全局配置在 PydanticFakerPlan 中传递，或从 AppState 中获取。

#### **3.3.3. 约束满足策略（直接、间接、自定义逻辑提示）**

Faker Engine 需要根据 PydanticFakerInstruction 中的信息来满足各种约束：

* **直接满足**: 大多数在 faker\_parameters 中定义的参数（如 min\_value, max\_value for pyint 14）可以直接传递给对应的 Faker Provider 方法。
* **间接满足 (非空约束)**: is\_nullable=False (默认) 意味着 Faker 方法将被调用以生成一个值。如果 is\_nullable=True 但随机判断结果为非空，则同样调用 Faker 方法。
* **自定义逻辑提示**: 当 instruction.custom\_logic\_description 存在时，意味着 LLM 认为该约束无法通过简单的 Faker Provider 调用和参数配置来满足。此时，Faker Engine 节点需要在初始 Faker 生成之后（或代替初始生成）执行相应的 Python 逻辑。instruction.dependencies 字段此时也变得非常重要。
  * 例如，对于约束 end\_date \> start\_date，LLM 的计划可能会为 end\_date 字段生成一条指令，其中 dependencies=\["start\_date"\]，custom\_logic\_description="确保结束日期在 start\_date 之后"。Faker Engine 在处理 end\_date 时，会首先查找当前行已生成的 start\_date 值，然后调用 fake.date\_between(start\_date=generated\_start\_date\_value) 或类似逻辑。
  * 对于更复杂的逻辑，如“值必须是质数”或一个 Faker regexify 难以处理的正则表达式，Faker Engine 可能先生成一个初步值，然后应用 custom\_logic\_description 中描述的 Python 验证逻辑。如果验证失败，可以尝试重新生成N次，或者记录错误并生成一个默认/标记值。

虽然 Faker 提供了众多 Provider 26，但复杂的字段间约束（如一个字段的值依赖于另一个字段的生成值）或高度定制化的验证规则，通常需要额外的 Python 代码来编排 Faker 调用或对 Faker 的输出进行后处理和验证 27。创建自定义 Faker Provider 也是一种高级选项，适用于需要频繁复用复杂生成逻辑的场景 15。有时，在数据生成后应用验证规则也是一种可行的策略 32。

**表 2：常见约束到 Faker 策略的映射指导 (供 LLM 参考)**

| 约束类型 (自然语言) | 目标 Pydantic 指令字段 | 示例 faker\_parameters 或自定义逻辑提示 (供 LLM 参考) | Faker 方法 (或逻辑) |
| :---- | :---- | :---- | :---- |
| X IS NOT NULL | is\_nullable=False | (默认) | (任意 Faker Provider) |
| X IS NULL (允许为空) | is\_nullable=True, null\_probability (例如 1.0 表示总是为空, 0.5 表示 50% 为空) | null\_probability=1.0 | (跳过 Faker 调用) |
| X \< 100 (整数) | faker\_provider="pyint", faker\_parameters | {"max\_value": 99} | pyint |
| X \> 10 (整数) | faker\_provider="pyint", faker\_parameters | {"min\_value": 11} | pyint |
| X \>= 10 AND X \<= 20 (整数) | faker\_provider="pyint", faker\_parameters | {"min\_value": 10, "max\_value": 20} | pyint |
| LENGTH(str\_X) \= 10 | faker\_provider="pystr", faker\_parameters | {"min\_chars": 10, "max\_chars": 10} | pystr |
| LENGTH(str\_X) \< 10 | faker\_provider="pystr", faker\_parameters | {"max\_chars": 9} (假设 min\_chars 为默认值或 0\) | pystr |
| X IN ('A', 'B', 'C') | faker\_provider="random\_element", faker\_parameters | {"elements":} | random\_element 14 |
| X LIKE 'PREFIX%' | faker\_provider="pystr\_format" (如果存在类似方法) 或 (faker\_provider="pystr", string\_format\_template, custom\_logic\_description) | {"string\_format": "PREFIX?????"} (若 pystr\_format 支持) 或 string\_format\_template="PREFIX?????" (使用 bothify) | pystr\_format 14 / bothify / pystr \+ Python 字符串拼接 |
| date\_X \> date\_Y | dependencies=\["date\_Y"\], faker\_provider="date\_between", custom\_logic\_description="确保 start\_date 是 date\_Y 的值" | Python 逻辑: start\_date \= get\_value("date\_Y"), then fake.date\_between(start\_date=start\_date\_plus\_1\_day) | date\_between (由 Python 逻辑包装调用) |
| X 必须是有效的邮箱地址 | faker\_provider="email" | {} | email |
| X 匹配正则表达式 "..." | faker\_provider="regexify", faker\_parameters 或 custom\_logic\_description | {"regex": "..."} 或 custom\_logic\_description="生成后根据正则表达式... 进行验证" | regexify / Python re 模块验证 |
| X 的格式为 'USER\_??\_\#\#\#\#' | faker\_provider="bothify", faker\_parameters (如果 LLM 判定 bothify 合适) 或 string\_format\_template | {"text": "USER\_??\_\#\#\#\#"} (对于 bothify) 或 string\_format\_template="USER\_??\_\#\#\#\#" | bothify 13 |

这张表格为 LLM Planner 提供了将自然语言约束转换为结构化 PydanticFakerInstruction 的具体指导。它弥合了人类可读规则与机器可执行的 Faker 调用之间的鸿沟，并明确了何时可能需要自定义 Python 逻辑。处理 dependencies 和 custom\_logic\_description 是 Faker Engine 节点超越简单循环的关键所在。它可能需要按特定顺序生成字段，或者为一个字段应用多步生成/验证逻辑。例如，如果 PydanticFakerInstruction 中包含 dependencies=\["start\_date"\] 和 custom\_logic\_description="must be after start\_date"，Faker Engine 在处理该字段时，会先获取当前行已生成的 start\_date 值，然后基于此值和描述中的逻辑（例如调用 fake.date\_between(start\_date=retrieved\_start\_date, end\_date='+1y')）来生成当前字段的值。这种机制使得系统能够处理更广泛和更复杂的约束条件。

### **3.4. 节点 3：JSON Outputter \- 结构化最终数据**

此节点负责将 Faker Engine 生成的中间数据（Python 字典列表）转换为用户要求的 JSON 格式。

它从 AppState 中获取 generated\_data\_intermediate，这是一个列表，其中每个元素是一个代表数据行的字典。然后，使用 Python 内置的 json 库将其序列化为 JSON 字符串，例如 json.dumps(state\['generated\_data\_intermediate'\], indent=2, ensure\_ascii=False) (其中 indent=2 用于美化输出，ensure\_ascii=False 用于正确处理中文字符)。最终的 JSON 字符串存储回 AppState 的 generated\_data\_json 字段。这是一个直接但关键的步骤，确保了最终输出的格式符合用户需求，并且易于被其他系统或工具消费。

### **3.5. 构建图：边、入口点和编译**

定义好状态和各个节点的功能后，接下来是使用 LangGraph 将它们组织成一个可执行的图：

1. 创建 StateGraph 实例:
   workflow \= StateGraph(AppState)
   这里 AppState 是之前定义的 TypedDict，作为图的全局状态模式 4。
2. 添加节点:
   将前面定义的三个核心功能函数注册为图中的节点：
   workflow.add\_node("llm\_planner", llm\_planner\_function)
   workflow.add\_node("faker\_engine", faker\_engine\_function)
   workflow.add\_node("json\_outputter", json\_outputter\_function)
3. 设置入口点:
   指定图的起始节点：
   workflow.set\_entry\_point("llm\_planner")
   当图被调用时，执行将从 llm\_planner 节点开始 9。
4. 定义边:
   连接节点，定义执行流程。对于这个核心任务，流程是线性的：
   workflow.add\_edge("llm\_planner", "faker\_engine")
   workflow.add\_edge("faker\_engine", "json\_outputter")
   workflow.add\_edge("json\_outputter", END)
   END 是 LangGraph 中的一个特殊节点，表示工作流程的结束 4。
5. 编译图:
   最后，编译工作流图，使其成为一个可调用的应用：
   app \= workflow.compile() 4

这个线性的图结构（Planner \-\> Engine \-\> Outputter）清晰地反映了数据转换的逻辑顺序，易于理解和可视化。虽然当前设计是线性的，但 LangGraph 的灵活性允许未来通过添加条件边来增强错误处理能力，例如，如果 LLM Planner 生成的计划无效，可以将流程导向一个错误处理节点或返回到 Planner 节点并附带反馈信息。

## **4\. 实践实施指南**

本节提供将上述设计转化为实际代码的关键步骤和示例片段。

### **4.1. LangGraph 与 Faker 环境设置**

首先，确保已安装必要的 Python 库。可以通过 pip 执行以下命令：

Bash

pip install langchain langgraph faker openai pydantic typing\_extensions

（注意：openai 是示例 LLM 提供商，可替换为其他如 langchain-anthropic 等。typing\_extensions 可能是一些 TypedDict 高级用法所必需的。）

同时，需要配置所选 LLM 提供商的 API 密钥。例如，对于 OpenAI，通常需要设置 OPENAI\_API\_KEY 环境变量 4。

### **4.2. Faker 执行计划的 Pydantic Schema (代码)**

在 3.2.3 节中概念性定义的 PydanticFakerInstruction 和 PydanticFakerPlan 模型，其实际 Python 代码如下。这是 LLM Planner 节点输出的结构，也是 Faker Engine 节点输入的依据。

Python

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PydanticFakerInstruction(BaseModel):
    field\_name: str \= Field(description="需要生成数据的字段的英文名称。")
    faker\_provider: str \= Field(description="要使用的 Python Faker provider 方法 (例如 'pyint', 'name', 'address', 'date\_between')。如果无法直接映射，则使用 'custom\_logic'。")
    faker\_parameters: Dict\[str, Any\] \= Field(default\_factory=dict, description="传递给 Faker provider 方法的参数字典。例如：pyint 的 {'min\_value': 0, 'max\_value': 99}。对于 date\_between，可使用 {'start\_date': '-1y', 'end\_date': 'today'}。")
    is\_nullable: bool \= Field(default=False, description="该字段是否可以为 null。如果为 True，还需考虑 null\_probability。")
    null\_probability: Optional\[float\] \= Field(default=0.0, description="如果 is\_nullable 为 True，则此字段生成 null 值的概率 (0.0 到 1.0)。")
    dependencies: Optional\[List\[str\]\] \= Field(default\_factory=list, description="此字段生成所依赖的其他 field\_name 列表 (用于复杂的字段间约束)。")
    custom\_logic\_description: Optional\[str\] \= Field(default=None, description="如果 Faker 无法通过 provider 和参数直接处理，则需要自定义逻辑或验证的自然语言描述。例如：'确保值是质数'，或 '结束日期必须在开始日期字段之后'。")
    string\_format\_template: Optional\[str\] \= Field(default=None, description="如果字段类型是字符串但需要特定格式 (例如 'ID-\#\#\#\#')，请提供模板。使用 \# 表示数字，? 表示字母。示例：'USER\_??\_\#\#\#\#'。")

class PydanticFakerPlan(BaseModel):
    plan\_description: str \= Field(default="使用 Python Faker 生成伪造数据的执行计划。", description="此计划的简要描述。")
    faker\_locale: Optional\[str\] \= Field(default=None, description="Faker 使用的区域设置，例如 'en\_US', 'zh\_CN'。如果可能，从输入上下文中确定。")
    instructions\_for\_fields: List\[PydanticFakerInstruction\] \= Field(description="指令列表，表中的每个字段对应一个指令。")

### **4.3. LangGraph 节点核心 Python 代码片段**

以下是每个 LangGraph 节点核心功能的 Python 伪代码或关键逻辑演示。

#### **4.3.1. llm\_planner\_function(state: AppState) \-\> AppState**

Python

from langchain\_openai import ChatOpenAI
\# 假设 AppState, TableFieldDefinition, PydanticFakerPlan 已定义

def llm\_planner\_function(state: AppState) \-\> AppState:
    \# 初始化 LLM
    \# 强烈建议使用支持结构化输出/JSON模式的较新模型
    llm \= ChatOpenAI(model="gpt-4o", temperature=0.1)
    structured\_llm \= llm.with\_structured\_output(PydanticFakerPlan) \# \[19, 20\]

    \# 构建提示
    \# 提示应包含角色定义、PydanticFakerPlan 的 schema 描述、
    \# 如何从 TableFieldDefinition 映射到 PydanticFakerInstruction 的指令和示例
    \# 以及如何处理各种约束的指导 (参考 表 2\)

    prompt\_parts \= \[
        "你是一个专家系统，负责将表结构定义和约束条件翻译成 Python Faker 库的执行计划。",
        "请根据以下Pydantic模型结构输出结果:",
        PydanticFakerPlan.model\_json\_schema(by\_alias=False), \# 提供 schema 定义给 LLM
        "\\n输入表结构定义如下:",
    \]
    for field\_def in state\['input\_table\_definitions'\]:
        prompt\_parts.append(f"- 字段中文名: {field\_def\['chinese\_name'\]}, 英文名: {field\_def\['english\_name'\]}, 类型: {field\_def\['field\_type'\]}, 样例: {field\_def\['sample\_value'\]}, 约束: {', '.join(field\_def\['constraints'\])}")

    if state.get('input\_constraints\_text'):
        prompt\_parts.append(f"\\n全局约束: {state\['input\_constraints\_text'\]}")

    prompt\_parts.append("\\n请为上述表结构生成 Faker 执行计划。")
    \# (此处应加入更多关于如何映射类型、约束到faker\_provider和faker\_parameters的详细指导和示例)
    \# 例如：对于INT类型，若有约束 'age \> 18 AND age \< 65'，则faker\_provider='pyint', faker\_parameters={'min\_value':19, 'max\_value':64}
    \# 对于VARCHAR类型，若有约束 'username IS NOT NULL', 则 is\_nullable=False
    \# 对于DATE类型，若有约束 'reg\_date \> "2022-01-01"', 则 faker\_provider='date\_between', faker\_parameters={'start\_date': '2022-01-02'}
    \# 对于 'department IN ('Sales', 'IT', 'HR')', 则 faker\_provider='random\_element', faker\_parameters={'elements':}
    \# 对于无法直接映射的复杂约束，请在 custom\_logic\_description 中描述。
    \# 如果输入包含中文字段名或样例，可以考虑将 faker\_locale 设置为 'zh\_CN'。

    final\_prompt \= "\\n".join(prompt\_parts)

    print("--- LLM Planner Prompt \---")
    print(final\_prompt)
    print("--------------------------")

    try:
        llm\_response\_plan \= structured\_llm.invoke(final\_prompt)
        updated\_state \= state.copy()
        updated\_state\['llm\_faker\_plan'\] \= llm\_response\_plan.model\_dump() \# 转换为 TypedDict 兼容格式
        updated\_state\['error\_message'\] \= None
        return updated\_state
    except Exception as e:
        print(f"LLM Planner 发生错误: {e}")
        updated\_state \= state.copy()
        updated\_state\['error\_message'\] \= f"LLM Planner 错误: {str(e)}"
        \# 可以考虑在此处设置一个特殊的计划，指示后续节点跳过或处理错误
        updated\_state\['llm\_faker\_plan'\] \= None
        return updated\_state

#### **4.3.2. faker\_engine\_function(state: AppState) \-\> AppState**

Python

from faker import Faker
import random
from datetime import datetime, timedelta, date

\# 假设 AppState, FakerExecutionPlan, FakerExecutionInstruction 已定义

def faker\_engine\_function(state: AppState) \-\> AppState:
    plan\_dict \= state.get('llm\_faker\_plan')
    if not plan\_dict:
        \# 如果没有计划 (可能因为LLM Planner出错)，则直接返回，或填充错误数据
        print("Faker Engine: 未找到执行计划，跳过生成。")
        updated\_state \= state.copy()
        updated\_state\['generated\_data\_intermediate'\] \=
        if not updated\_state.get('error\_message'): \# 避免覆盖LLM Planner的错误
             updated\_state\['error\_message'\] \= "Faker Engine: 执行计划缺失。"
        return updated\_state

    \# 将 TypedDict 转换回 Pydantic 模型以便于访问
    try:
        plan \= PydanticFakerPlan(\*\*plan\_dict)
    except Exception as e:
        print(f"Faker Engine: 无法解析执行计划: {e}")
        updated\_state \= state.copy()
        updated\_state\['generated\_data\_intermediate'\] \=
        updated\_state\['error\_message'\] \= f"Faker Engine: 执行计划解析失败 \- {str(e)}"
        return updated\_state

    fake \= Faker(locale=plan.faker\_locale if plan.faker\_locale else None)
    \# 可在此处设置全局种子: Faker.seed(0) or fake.seed\_instance(0)

    num\_rows \= state\['num\_rows\_to\_generate'\]
    generated\_rows \=

    \# 用于处理字段间依赖的缓存
    \# 在生成依赖字段时，需要确保被依赖字段已在此次迭代中生成
    \# 可以对 instructions\_for\_fields 进行拓扑排序，或在循环中按需生成

    \# 简单的处理方式：假设依赖关系不复杂，或LLM已合理安排顺序
    \# 更健壮的方式：构建依赖图，按顺序生成

    for \_ in range(num\_rows):
        current\_row\_data: Dict\[str, Any\] \= {}

        \# 按照LLM计划中的字段顺序处理
        \# 如果有复杂的依赖关系，LLM Planner应尝试将依赖项放在前面，
        \# 或者Faker Engine需要实现更复杂的依赖解析和执行顺序控制。

        \# 第一遍：生成没有依赖或依赖已满足的字段
        \# (简化版：此处未实现完整的依赖排序，仅为演示基本调用)

        for instruction\_model in plan.instructions\_for\_fields:
            \# 将 TypedDict instruction 转换为 Pydantic model
            instruction \= PydanticFakerInstruction(\*\*instruction\_model)
            field\_name \= instruction.field\_name

            if instruction.is\_nullable and random.random() \< (instruction.null\_probability or 0.0):
                current\_row\_data\[field\_name\] \= None
                continue

            \# 处理依赖和自定义逻辑
            \# 这是一个简化的示例，实际应用中可能需要更复杂的逻辑来处理依赖和自定义规则
            if instruction.custom\_logic\_description:
                \# 示例：如果 end\_date 依赖于 start\_date
                if "end\_date" in field\_name.lower() and "start\_date" in (instruction.custom\_logic\_description or "").lower() and instruction.dependencies and "start\_date" in instruction.dependencies:
                    start\_date\_val \= current\_row\_data.get(instruction.dependencies) \# 假设依赖列表中第一个是start\_date
                    if isinstance(start\_date\_val, (date, datetime)):
                        \# 确保 end\_date 在 start\_date 之后
                        try:
                            \# 尝试从参数中获取 end\_date 的相对范围，否则默认
                            end\_delta\_days \= instruction.faker\_parameters.get("days\_after\_start", 365)
                            current\_row\_data\[field\_name\] \= fake.date\_between\_dates(date\_start=start\_date\_val \+ timedelta(days=1), date\_end=start\_date\_val \+ timedelta(days=1 \+ int(end\_delta\_days)))
                        except Exception as e:
                             current\_row\_data\[field\_name\] \= f"Error generating dependent date: {e}"
                        continue \# 跳过通用 provider 调用
                    else: \# start\_date 未生成或类型不对
                        current\_row\_data\[field\_name\] \= "Error: start\_date dependency not met"
                        continue
                \# 其他自定义逻辑可在此处扩展
                \# 如果 custom\_logic\_description 存在但未被特殊处理，可以考虑记录警告或尝试默认行为

            try:
                if instruction.string\_format\_template:
                    \# 假设LLM会指定使用bothify或regexify，或我们根据模板特征选择
                    \# 这里简化为 bothify
                    current\_row\_data\[field\_name\] \= fake.bothify(text=instruction.string\_format\_template)
                elif instruction.faker\_provider \== "custom\_logic":
                    \# 如果 provider 是 'custom\_logic'，表示LLM希望我们完全依赖 description
                    \# 这里可以填充一个占位符或尝试解析 description 来执行特定操作
                    current\_row\_data\[field\_name\] \= f"Custom logic needed: {instruction.custom\_logic\_description}"
                else:
                    provider\_method \= getattr(fake, instruction.faker\_provider)
                    current\_row\_data\[field\_name\] \= provider\_method(\*\*instruction.faker\_parameters)
            except AttributeError:
                current\_row\_data\[field\_name\] \= f"Error: Unknown Faker provider '{instruction.faker\_provider}'"
            except Exception as e:
                current\_row\_data\[field\_name\] \= f"Error generating data for {field\_name} using {instruction.faker\_provider}: {str(e)}"

        generated\_rows.append(current\_row\_data)

    updated\_state \= state.copy()
    updated\_state\['generated\_data\_intermediate'\] \= generated\_rows
    updated\_state\['error\_message'\] \= None \# 清除或更新错误信息
    return updated\_state

#### **4.3.3. json\_outputter\_function(state: AppState) \-\> AppState**

Python

import json
\# 假设 AppState 已定义

def json\_outputter\_function(state: AppState) \-\> AppState:
    intermediate\_data \= state.get('generated\_data\_intermediate',)
    try:
        \# ensure\_ascii=False 保证中文字符正确显示，而不是被转义
        json\_output \= json.dumps(intermediate\_data, indent=2, ensure\_ascii=False)
        updated\_state \= state.copy()
        updated\_state\['generated\_data\_json'\] \= json\_output
        updated\_state\['error\_message'\] \= None
    except Exception as e:
        print(f"JSON Outputter 发生错误: {e}")
        updated\_state \= state.copy()
        updated\_state\['generated\_data\_json'\] \= ""
        updated\_state\['error\_message'\] \= f"JSON Outputter 错误: {str(e)}"
    return updated\_state

### **4.4. 调用和运行数据生成图**

Python

from langgraph.graph import StateGraph, END

\# (在此处导入 AppState, TableFieldDefinition, 以及节点函数)
\#... llm\_planner\_function, faker\_engine\_function, json\_outputter\_function...

\# 1\. 定义图
workflow \= StateGraph(AppState)
workflow.add\_node("llm\_planner", llm\_planner\_function)
workflow.add\_node("faker\_engine", faker\_engine\_function)
workflow.add\_node("json\_outputter", json\_outputter\_function)

workflow.set\_entry\_point("llm\_planner")
workflow.add\_edge("llm\_planner", "faker\_engine")
workflow.add\_edge("faker\_engine", "json\_outputter")
workflow.add\_edge("json\_outputter", END)

app \= workflow.compile()

\# 2\. 准备初始状态
initial\_table\_definitions: List \=},
    {"chinese\_name": "用户名", "english\_name": "username", "field\_type": "VARCHAR(50)", "sample\_value": "zhang\_san", "constraints":},
    {"chinese\_name": "年龄", "english\_name": "age", "field\_type": "INT", "sample\_value": "25", "constraints": \["age \> 18", "age \< 65"\]},
    {"chinese\_name": "邮箱", "english\_name": "email", "field\_type": "VARCHAR(100)", "sample\_value": "test@example.com", "constraints":},
    {"chinese\_name": "注册日期", "english\_name": "reg\_date", "field\_type": "DATE", "sample\_value": "2023-01-15", "constraints": \["reg\_date \> '2022-01-01'"\]},
    {"chinese\_name": "部门", "english\_name": "department", "field\_type": "VARCHAR(20)", "sample\_value": "Sales", "constraints":},
    {"chinese\_name": "订单号", "english\_name": "order\_id", "field\_type": "VARCHAR(10)", "sample\_value": "ORD-001", "constraints":} \# 示例自定义格式约束
\]

initial\_state: AppState \= {
    "input\_table\_definitions": initial\_table\_definitions,
    "input\_constraints\_text": None, \# 可选的全局约束
    "llm\_faker\_plan": None, \# 初始化为空
    "generated\_data\_intermediate":, \# 初始化为空列表
    "generated\_data\_json": "", \# 初始化为空字符串
    "error\_message": None, \# 初始化为无错误
    "num\_rows\_to\_generate": 5 \# 指定生成5行数据
}

\# 3\. 调用图
\# 对于流式输出，可以使用 app.stream(initial\_state)
\# final\_state \= app.invoke(initial\_state)

\# 迭代地查看每个步骤的输出
for s in app.stream(initial\_state, {"recursion\_limit": 10}): \# 设置递归限制
    print(f"--- 当前节点: {list(s.keys())} \---")
    \# print(s) \# 打印当前节点的完整状态更新
    if 'llm\_faker\_plan' in s.get(list(s.keys()), {}):
        print("LLM Faker Plan:")
        \# 为了可读性，可以格式化打印 PydanticFakerPlan
        plan\_data \= s\[list(s.keys())\]\['llm\_faker\_plan'\]
        if plan\_data:
            try:
                \# 尝试用Pydantic模型美化打印
                p\_plan \= PydanticFakerPlan(\*\*plan\_data)
                print(json.dumps(p\_plan.model\_dump(), indent=2, ensure\_ascii=False))
            except:
                print(json.dumps(plan\_data, indent=2, ensure\_ascii=False))
        else:
            print("Plan is None.")

    if 'generated\_data\_json' in s.get(list(s.keys()), {}):
        final\_json\_output \= s\[list(s.keys())\]\['generated\_data\_json'\]
        if final\_json\_output:
            print("\\n--- 最终生成的 JSON 数据 \---")
            print(final\_json\_output)

    if 'error\_message' in s.get(list(s.keys()), {}) and s\[list(s.keys())\]\['error\_message'\]:
        print(f"错误信息: {s\[list(s.keys())\]\['error\_message'\]}")
        break \# 如果有错误，可以提前终止

\# 或者，如果只想获取最终结果：
\# config \= {"recursion\_limit": 10} \# 确保设置递归限制
\# final\_result\_map \= app.invoke(initial\_state, config=config)
\# final\_json\_output \= final\_result\_map.get("generated\_data\_json", "")
\# if final\_json\_output:
\#     print("\\n--- 最终生成的 JSON 数据 \---")
\#     print(final\_json\_output)
\# if final\_result\_map.get("error\_message"):
\#     print(f"错误: {final\_result\_map\['error\_message'\]}")

在运行上述代码前，请确保已正确设置 OPENAI\_API\_KEY 环境变量，并且所有必要的类（如 AppState, PydanticFakerPlan 等）和函数都已定义。

## **5\. 高级技术与最佳实践**

为了构建一个更健壮、灵活和高效的测试数据生成系统，可以考虑以下高级技术和最佳实践。

### **5.1. 稳健的错误处理和输入验证**

一个生产级的系统必须能够优雅地处理各种预料之外的情况。

* **输入验证**: 在将用户提供的表结构定义传递给 LLM Planner 之前，应进行初步的结构和类型验证。例如，确保每个字段定义都包含必需的键（如 english\_name, field\_type），并且字段类型是已知的或可处理的。
* **LLM 输出验证**: PydanticFakerPlan 和 PydanticFakerInstruction 的使用本身就提供了一层强大的 schema 验证 22。如果 LLM 的输出不符合此 schema，with\_structured\_output 机制通常会尝试修正或抛出错误。在此情况下，可以设计重试逻辑（例如，向 LLM 提供错误信息并要求其修正计划），或者将流程导向一个错误处理节点，记录问题并终止。
* **Faker Engine 错误**: 在 Faker Engine 节点中，动态调用 Faker Provider 时可能会发生错误，例如 LLM 计划指定了一个不存在的 Provider，或者提供的参数对于某个 Provider 无效。应使用 try-except 块捕获这些异常，记录详细错误信息，并决定是为该字段生成一个默认值/错误标记，还是中止整行或整个批次数据的生成。
* **LangGraph 错误状态与条件边**: 可以在 AppState 中增加专门的错误信息字段。通过在图中引入条件边，可以根据这些错误信息将执行流程导向特定的错误处理节点。例如，如果 llm\_planner\_function 将错误信息写入状态，一个条件边可以判断此信息是否存在，若存在则转到一个记录日志并终止的节点，而不是继续执行 faker\_engine\_function。

实施这些错误处理机制，能够显著提高系统的可靠性，并在出现问题时提供更清晰的诊断信息。

### **5.2. 管理复杂和字段间约束**

处理复杂的约束，特别是那些涉及多个字段之间关系的约束，是数据生成中的一个主要挑战。

* **LLM 驱动的依赖声明与排序**: 对于相对简单的字段间依赖（例如 end\_date 必须在 start\_date 之后），LLM 可以在 PydanticFakerInstruction 的 dependencies 字段中声明这种依赖关系，并在 custom\_logic\_description 中提供处理逻辑的提示。Faker Engine 节点随后需要确保字段的生成顺序遵循这些依赖关系。这可能涉及到对 instructions\_for\_fields 列表进行拓扑排序，或者在生成循环中，如果一个字段的依赖项尚未生成，则先生成依赖项。
* **自定义 Faker Provider**: 当某种复杂的、领域特定的数据生成逻辑需要被频繁复用时，创建一个自定义的 Faker Provider 是一个整洁且高效的解决方案 6。例如，可以创建一个 FiscalPeriodProvider 来生成符合特定财年规则的开始和结束日期。LLM Planner 随后可以直接在其计划中指定使用这个自定义 Provider 的名称。
* **生成后验证与过滤**: 对于那些在生成过程中极难或无法高效实施的非常复杂的业务规则（例如，涉及跨多行的聚合约束，或需要复杂计算的校验），一种策略是先生成一个略微宽松或稍大数据量的候选数据集，然后通过独立的 Python 脚本或在 LangGraph 中增加一个后处理节点，对生成的数据进行验证和过滤，剔除不符合最终复杂约束的数据行 29。这种方法虽然可能牺牲一些生成效率，但对于确保最终数据的合规性可能更为直接。
* **LLM 辅助的迭代细化**: 对于极其复杂的场景，可以设想一个更高级的迭代流程：首先生成一批数据，然后使用另一个 LLM（或同一 LLM 的不同提示）来评估生成的数据是否满足所有约束。如果发现不符合项，可以将反馈信息传递给 LLM Planner，让其尝试修正 Faker 执行计划，然后进行下一轮数据生成。这构成了一个闭环反馈系统，但其实现复杂度较高，可能超出初始设计范围。

在 LLM 的声明式规划能力与 Faker Engine 中 Python 代码的程序化执行能力之间取得平衡是关键。custom\_logic\_description 和 dependencies 字段为这种平衡提供了桥梁，允许系统优雅地处理那些超出简单参数化 Faker Provider 能力范围的约束。

### **5.3. 确保幂等性和可复现性 (Faker 播种)**

在测试数据生成中，尤其是用于自动化测试或问题复现时，确保生成过程的可复现性至关重要。如果一个测试用例因为某批特定的生成数据而失败，开发者需要能够精确地重新生成这批数据以进行调试。

Python Faker 库通过播种（seeding）其内部的随机数生成器来支持可复现性 5。可以通过以下方式实现：

* Faker.seed(seed\_value): 这是一个类方法，会为所有 Faker 实例设置一个共享的种子。
* fake.seed\_instance(seed\_value): 这是一个实例方法，仅为特定的 fake 对象设置种子。

在我们的 LangGraph 应用中，可以将种子值作为初始 AppState 的一部分传入，或者作为一个全局配置项。Faker Engine 节点在初始化 Faker 实例时，或者在每次生成新的一批数据之前，使用这个种子值。这样，只要输入的表结构、约束和种子值相同，生成的数据集也将保持一致。

### **5.4. 优化 LLM 提示以提高准确性和效率**

LLM Planner 节点的性能（即其生成 Faker 执行计划的准确性和合理性）高度依赖于提示的质量。

* **少样本示例 (Few-Shot Examples)**: 在提示中包含 2-3 个多样化的输入输出示例对，能够显著提升 LLM 的理解和表现 1。每个示例应展示一个具体的表结构定义（可能包含一些约束）以及期望 LLM 输出的对应 PydanticFakerPlan JSON 结构。
* **清晰性和特指性**: 提示中的指令必须清晰、明确，避免歧义 17。例如，在解释如何将特定类型的约束（如范围、枚举、格式）映射到 Faker 参数时，应提供具体的转换规则和期望的参数格式。
* **迭代测试与细化**: LLM 提示工程本身是一个迭代的过程。应将 LLM Planner 节点作为一个独立的单元进行测试，输入各种不同的表结构和约束组合，观察其生成的计划。根据观察到的错误、不一致或次优的计划，不断调整和优化提示内容。
* **温度参数 (Temperature Setting)**: 在调用 LLM 时，将其 temperature 参数设置为一个较低的值（例如 0.0 到 0.2 之间）25。较低的温度会使 LLM 的输出更具确定性和一致性，这对于生成结构化且可预测的执行计划通常是期望的。较高的温度会导致更多样化和创造性的输出，但可能牺牲准确性。

投入时间进行提示的测试和迭代优化，对于确保整个数据生成系统的准确性和鲁棒性至关重要。

## **6\. 结论与未来展望**

### **6.1. 方案回顾及其优势**

本文提出并详细设计了一种利用大型语言模型（LLM）、LangGraph 框架和 Python Faker 库来智能化生成仿真测试数据的系统。该系统通过 LLM Planner 节点解析用户提供的表结构定义和自然语言约束，生成结构化的 Faker 执行计划；Faker Engine 节点根据此计划调用 Faker 库生成数据；最终由 JSON Outputter 节点将数据格式化为 JSON 输出。整个流程通过 LangGraph 进行编排，实现了模块化和状态管理。

该方案的主要优势包括：

* **智能化与自动化**: LLM 的引入使得系统能够理解自然语言描述的复杂需求，自动化了从需求到可执行计划的转换过程。
* **灵活性与可扩展性**: LangGraph 的图结构和节点化设计使得添加新功能、修改现有逻辑或集成其他工具变得相对容易。Faker 库本身也具有良好的可扩展性（如自定义 Provider）。
* **约束处理能力**: 通过结合 LLM 的规划、Pydantic schema 的结构化以及 Faker Engine 中的 Python 逻辑，系统能够处理包括字段内约束、格式约束、非空约束以及一定程度的字段间依赖在内的多种约束条件。
* **可控性与可维护性**: LangGraph 的状态管理和清晰的节点边界有助于理解数据流和调试问题。Pydantic 模型确保了节点间数据传递的规范性。

### **6.2. 潜在的增强方向**

当前设计的系统提供了一个坚实的基础，未来可以从以下几个方面进行增强和扩展：

* **批量处理与大规模数据生成**: 优化 Faker Engine 以支持更高效地生成大量数据行，并支持将结果输出到多个文件或直接写入数据库。
* **用户界面集成**: 开发一个简单的图形用户界面（例如使用 Streamlit 10 或 Flask/Django），允许用户通过表单输入表结构定义、约束条件和生成参数，并能在线查看或下载生成的 JSON 数据。
* **增强复杂约束处理**:
  * 进一步提升 LLM Planner 对更复杂字段间依赖（例如，涉及三个或更多字段的条件逻辑，或基于统计分布的依赖）的理解和规划能力。
  * 在 Faker Engine 中实现更完善的依赖解析和执行调度逻辑。
  * 集成更高级的约束求解器或规则引擎。
* **LLM 反馈与计划修正循环**: 实现一个反馈机制，如果 Faker Engine 在执行计划时遇到问题，或者生成的数据未能通过最终的复杂验证，可以将错误信息或不符合项反馈给 LLM Planner，请求其修正原计划并重新尝试。
* **支持更多输出格式**: 除了 JSON，还可以增加对 CSV、XML、SQL INSERT 语句等常见数据格式的输出支持。这将需要一个新的输出转换节点或对现有 JSON Outputter 进行扩展。
* **人机协作 (Human-in-the-Loop) 进行计划审查**: 在 LLM Planner 生成 Faker 执行计划后，可以引入一个 LangGraph 节点，允许人工审查和修改该计划，然后再提交给 Faker Engine 执行 3。这对于确保关键或复杂数据生成的准确性非常有价值。
* **集成真实数据分析以指导生成**: 允许用户提供少量真实数据样本，系统可以分析这些样本的统计特性（如数据分布、字段相关性），并指导 LLM Planner 和 Faker Engine 生成更逼近真实世界数据的仿真数据。

综上所述，将 LLM 的智能规划能力与 LangGraph 的流程控制以及 Faker 的数据模拟能力相结合，为解决复杂测试数据生成问题提供了一条富有前景的技术路径。随着相关技术的不断发展，此类智能化数据生成系统将在提升软件测试效率和质量方面发挥越来越重要的作用。

#### **引用的著作**

1. Prompt Patterns for Structured Data Extraction from Unstructured Text, 访问时间为 五月 28, 2025， [https://www.cs.wm.edu/\~dcschmidt/PDF/Prompt\_Patterns\_for\_Structured\_Data\_Extraction\_from\_Unstructured\_Text\_\_\_Final.pdf](https://www.cs.wm.edu/~dcschmidt/PDF/Prompt_Patterns_for_Structured_Data_Extraction_from_Unstructured_Text___Final.pdf)
2. LLM Agents \- Prompt Engineering Guide, 访问时间为 五月 28, 2025， [https://www.promptingguide.ai/research/llm-agents](https://www.promptingguide.ai/research/llm-agents)
3. LangGraph basics \- Overview, 访问时间为 五月 28, 2025， [https://langchain-ai.github.io/langgraph/concepts/why-langgraph/](https://langchain-ai.github.io/langgraph/concepts/why-langgraph/)
4. GenAI\_Agents/all\_agents\_tutorials/langgraph-tutorial.ipynb at main \- GitHub, 访问时间为 五月 28, 2025， [https://github.com/NirDiamant/GenAI\_Agents/blob/main/all\_agents\_tutorials/langgraph-tutorial.ipynb](https://github.com/NirDiamant/GenAI_Agents/blob/main/all_agents_tutorials/langgraph-tutorial.ipynb)
5. Python Faker Library \- Tutorialspoint, 访问时间为 五月 28, 2025， [https://www.tutorialspoint.com/python/python\_faker\_library.htm](https://www.tutorialspoint.com/python/python_faker_library.htm)
6. Faker is a Python package that generates fake data for you. \- GitHub, 访问时间为 五月 28, 2025， [https://github.com/xfxf/faker-python](https://github.com/xfxf/faker-python)
7. Generate Realistic Sample Data Easily with Python's Faker \- Toolify.ai, 访问时间为 五月 28, 2025， [https://www.toolify.ai/ai-news/generate-realistic-sample-data-easily-with-pythons-faker-609813](https://www.toolify.ai/ai-news/generate-realistic-sample-data-easily-with-pythons-faker-609813)
8. Introduction to LangGraph \- Neural Nonsense, 访问时间为 五月 28, 2025， [https://mojtabamaleki.hashnode.dev/introduction-to-langgraph](https://mojtabamaleki.hashnode.dev/introduction-to-langgraph)
9. StateGraph (Graph API) \- Overview, 访问时间为 五月 28, 2025， [https://langchain-ai.github.io/langgraph/concepts/low\_level/](https://langchain-ai.github.io/langgraph/concepts/low_level/)
10. LangGraph Tutorial for Beginners to Build AI Agents \- ProjectPro, 访问时间为 五月 28, 2025， [https://www.projectpro.io/article/langgraph/1109](https://www.projectpro.io/article/langgraph/1109)
11. Complete Guide to Building LangChain Agents with the LangGraph Framework \- Zep, 访问时间为 五月 28, 2025， [https://www.getzep.com/ai-agents/langchain-agents-langgraph](https://www.getzep.com/ai-agents/langchain-agents-langgraph)
12. LangGraph Uncovered: Building Stateful Multi-Agent Applications with LLMs-Part I, 访问时间为 五月 28, 2025， [https://dev.to/sreeni5018/langgraph-uncovered-building-stateful-multi-agent-applications-with-llms-part-i-p86](https://dev.to/sreeni5018/langgraph-uncovered-building-stateful-multi-agent-applications-with-llms-part-i-p86)
13. Generate custom datasets using Python Faker \- SAP Community, 访问时间为 五月 28, 2025， [https://community.sap.com/t5/technology-blogs-by-sap/generate-custom-datasets-using-python-faker/ba-p/13511383](https://community.sap.com/t5/technology-blogs-by-sap/generate-custom-datasets-using-python-faker/ba-p/13511383)
14. faker.providers.python — Faker 37.3.0 documentation, 访问时间为 五月 28, 2025， [https://faker.readthedocs.io/en/master/providers/faker.providers.python.html](https://faker.readthedocs.io/en/master/providers/faker.providers.python.html)
15. joke2k/faker: Faker is a Python package that generates fake data for you. \- GitHub, 访问时间为 五月 28, 2025， [https://github.com/joke2k/faker](https://github.com/joke2k/faker)
16. Dynamic Providers for Faker \- Avo Pisikyan, 访问时间为 五月 28, 2025， [https://avop.me/blog/dynamic-providers-for-faker/](https://avop.me/blog/dynamic-providers-for-faker/)
17. The Complete Conversation LLM Prompt Creation Guide | 2025 \- Tavus, 访问时间为 五月 28, 2025， [https://www.tavus.io/post/llm-prompt](https://www.tavus.io/post/llm-prompt)
18. Prompts Tips & Best Practices \- Gretel.ai, 访问时间为 五月 28, 2025， [https://docs.gretel.ai/playground/prompts-tips-and-best-practices](https://docs.gretel.ai/playground/prompts-tips-and-best-practices)
19. Structured Outputs from LLMs with LangChain \- Opcito, 访问时间为 五月 28, 2025， [https://www.opcito.com/blogs/langchain-for-clean-object-based-responses-from-llmss](https://www.opcito.com/blogs/langchain-for-clean-object-based-responses-from-llmss)
20. Structured outputs | 🦜️ LangChain, 访问时间为 五月 28, 2025， [https://python.langchain.com/docs/concepts/structured\_outputs/](https://python.langchain.com/docs/concepts/structured_outputs/)
21. How to Use a Single Pydantic Model for Structured Output with Long Documents in a Chunked RAG Pipeline? \- OpenAI Developer Community, 访问时间为 五月 28, 2025， [https://community.openai.com/t/how-to-use-a-single-pydantic-model-for-structured-output-with-long-documents-in-a-chunked-rag-pipeline/1080681](https://community.openai.com/t/how-to-use-a-single-pydantic-model-for-structured-output-with-long-documents-in-a-chunked-rag-pipeline/1080681)
22. A Fun PydanticAI Example For Automating Your Life \- Christopher Samiullah, 访问时间为 五月 28, 2025， [https://christophergs.com/blog/pydantic-ai-example-github-actions](https://christophergs.com/blog/pydantic-ai-example-github-actions)
23. Think Inside the JSON: Reinforcement Strategy for Strict LLM Schema Adherence \- arXiv, 访问时间为 五月 28, 2025， [https://arxiv.org/html/2502.14905v1](https://arxiv.org/html/2502.14905v1)
24. Learning to Generate Structured Output with Schema Reinforcement Learning \- arXiv, 访问时间为 五月 28, 2025， [https://arxiv.org/html/2502.18878v1](https://arxiv.org/html/2502.18878v1)
25. Taming LLMs with Langchain \+ Langgraph \- HackerNoon, 访问时间为 五月 28, 2025， [https://hackernoon.com/taming-llms-with-langchain-langgraph](https://hackernoon.com/taming-llms-with-langchain-langgraph)
26. Standard Providers — Faker 37.3.0 documentation, 访问时间为 五月 28, 2025， [https://faker.readthedocs.io/en/master/providers.html](https://faker.readthedocs.io/en/master/providers.html)
27. How to Generate Realistic Data for Machine Learning using Python \- Index.dev, 访问时间为 五月 28, 2025， [https://www.index.dev/blog/simulate-realistic-data-python-ml](https://www.index.dev/blog/simulate-realistic-data-python-ml)
28. Using faker and pandas Python Libraries to Create Synthetic Data for Testing, 访问时间为 五月 28, 2025， [https://dev.to/rahulbhave/using-faker-and-pandas-python-libraries-to-create-synthetic-data-for-testing-4gn4](https://dev.to/rahulbhave/using-faker-and-pandas-python-libraries-to-create-synthetic-data-for-testing-4gn4)
29. Creating Fake Data in Python Using Faker \- Udacity, 访问时间为 五月 28, 2025， [https://www.udacity.com/blog/2023/03/creating-fake-data-in-python-using-faker.html](https://www.udacity.com/blog/2023/03/creating-fake-data-in-python-using-faker.html)
30. Creating a custom provider for faker with user-specified weights \- gavincampbell.dev, 访问时间为 五月 28, 2025， [https://gavincampbell.dev/post/python-faker-weighted-custom-provider/](https://gavincampbell.dev/post/python-faker-weighted-custom-provider/)
31. Faker providers for project specific data structure fakes, in Python \- gotofritz.net, 访问时间为 五月 28, 2025， [https://gotofritz.net/blog/create-fake-dataset-fixtures-testing-with-faker/](https://gotofritz.net/blog/create-fake-dataset-fixtures-testing-with-faker/)
32. 3 methods for email validation using Python (tutorial and code) \- MailerCheck, 访问时间为 五月 28, 2025， [https://www.mailercheck.com/articles/email-validation-using-python](https://www.mailercheck.com/articles/email-validation-using-python)