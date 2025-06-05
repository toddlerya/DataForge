# 数据仿真生成器

## 一图概览

[Meriad在线编辑](https://mermaid.live/edit#pako:eNqdWAtv2lYU_iuWJ0WrBBGEhIA3TQNsOlYCKZB1DybkwuWxGBsZsyxLIjVV0q5ro2ZLu77SJmxrG61aEm1q04W2-S8bNvRf7Fzb2NhASCpFIvY933eOv3se114gs0IOkRTpdDrTvFSSOEQRNCuxYUEsIMJJBCLNxlFrc0u5va-s7bZubSk_rMsHj-XVgzSfFfh8qUCleYLgBGGWIoosn6NFdo7Ht6QiKgMZL4hlllNt2HmhJlEE4mbxJfyoUIIoI_DF5AqoShF5lqsi7TYPkU1zbBZoeCkpiayECvMUEWNSF-KJc5lkZGo6ynyu2WbnsxwKioidLfEFbIstp-I0E83EEzSTSPPqA-Y5YS5bZEWJSNEaMJkKJFIfL1SLbAWCzZZE4HFAqBcRRxFpsiqBcZpc0oyZGD3YFBYNw0hseiaVSQWCUYaiqJkqEiN8pSaFOLZaNRjKLF9jOWcJr3TxKCD25gNN6XZ9R15faz3dtzEnz0dPzdt8eV_-sa5sPW7v_Qr4NEnolNHoVBLY4MfKUxGFbLWLAAyUzTXgSKf592mEKlWEZv-7tHz-AuLPGAFOBxJJJhOKRzPTifjUNKjAwD4FUlgICZUrHGyj7ofQHeWEbJcb-c87yu5z5e62vL8i15_Jq6vKzfXW74ftvTVlp648PBroCjxAzOWKZOMXcrmT8ZuamNSBs5BwwMwWIAutAnEl3imirHQseQDjTOJkAGdthg6kAl8Z5tsHzTfXtQp7--BKmvwa_JXKFUGUWN2nBj7LxN5VVb2Kn19v793uruUebTuBmr5OJutQB1bqcOCcpgIIzMTsAhODFR7kx6azya8pDg7ooHX7hhKre9HDRwf7cOFAs_PcsXTyn3flyzvy4YaFNAFShFLxxBeZJJP4jEkAebwmJZH4LRKtPiS2MECMbrk7Fdo-fNZsvG7vLUOFKteuK5uH8s0D-F_e3JdfXm69-qW1vWzKNUOHM6FPmNC5UwZQy-Xlq69xANeetus3dO8GrSrYFINVi4eSfZiJwdRA2mxstHC_ugKima0HmmKrsaE8WpF_vqH81WitX2k2GrAGTe2M6VptvmoFR2LhOLguI4nt3TRrleB-q5Zk86iuLO-ZbJ_Gg7jpnoZLCw1Adi7Mo_aXxOkEAVz76W_Ko3W7ypgwFI_RkVQkHusbnY1prohEpDysNxsvNIZvhBLffW1sq6aGdvPfS0_gz0jeaCB2diacxJUVZflCuFZFw5-hY9l68BOUhrKype7vSvPVvvk48ZmUOuM65WDU2vHJAiXQfrMhXz2U7-2YZHpSv2OXUVmV7frbP27Y-kvX6YFwOj_qnvjWtVFjEbZJNTX3n-g5LagG1qrpV0mqmTXDiRFLkvamrd1359LInDQ_ZIKDC5tPzGE3t91U52ffoUp8iC3x6QOI-7XC_ig1bnOKdqK2PIpNjN7AR_rNUpXavG9c2mZVzyA_3rDPgvnkg02whX2I4We1pvW7Hge6M3vQ8crm42THgL7EveXYJ7VOt4FYHhtZ_8EPUJudBWvux6IWtDZGW_dX9Ce5uyevP1Ea9faLv6ErEl2tc7F7avbpNvZdti6aHt9eut8-uiqvPoYpp50RFi3HDfue6_hRg6D5ck3jUO68aDXuQQtsHu0qt_6RG4ft3d3Fvuk10luivQcdVSlLO1bv4DcdfnDmjtgiHektYdwUO_OjQ5XFaUWjPGG2aCJf4jjqvbw_78gLvOScQ6VCUaIuClzuAxvIelzWgV6G9vjd4fBQtKVmdHCQYbw-n284uKsqdKjPQ0-6mBNArdO_E3Uo5Ge8Qd9QdOeNTccxPtrjc_tcQ3HG-cAAAuwkQH0SdwQK-twAHQ6zHA90sMvlCYaZicmhYOtLro6mA7R3gvEFetGkgywjscyWciRFLmCuNKl-iUiTuD3lUJ6tcTDH0_wSmLI1SUjO81mSksQacpCiUCsUSUr9COEga5Uc5ARdYgsiW-6YVFj-S0EwLlGuJAnilPYRRf2W4iALIvauMyI-B9sr1HiJpMbGx1UCklogv4PLSf-oy-Oe8LkmvW6v3-uH1XmS8oyN-sf8_kkXmPu8bs_EkoP8XnXpGvWNeTze8XG_d8zjdk363Uv_Awp3lrQ)


```mermaid
---
title: DataForge - AI仿真数据生成工具
config:
  look: handDrawn
  theme: normal
  layout: elk
  elk:
    mergeEdges: false
    nodePlacementStrategy: NETWORK_SIMPLEX
    cycleBreakingStragy: MODEL_ORDER
---

flowchart TD
    START@{shape: circle, label: "start"}
    END@{shape: circle, label: "END"}
    INPUT_TABLE:::UserInputClass@{shape: manual-input, label: "期望生成表名称"}
    INPUT_SQL:::UserInputClass@{shape: manual-input, label: "业务查询SQL" }
    LLMS:::LLMClass@{shape: procs, label: "LLM服务\n(Deepseek、QWen)"}
    PARSE_COL_PROMPT_TEMPLATE:::templateClass@{ shape: doc, label: "字段映射填充提示词模板"}
    PARSE_COL_PROMPT:::promptClass@{ shape: odd, label: "字段映射填充提示词" }
    PARSE_COL_AGNET:::agentClass@{shape: lin-rect, label: "字段映射填充Agent" }
    SAMPLE_DATA["字段样例数据集"]:::importantClass
    GEN_PROMPT_TEMPLATE:::templateClass@{ shape: doc, label: "仿真测试数据生成提示词模板" }
    GEN_PROMPT:::promptClass@{ shape: odd, label: "仿真测试数据生成提示词" }
    GEN_FAKE_DATA_AGENT:::agentClass@{ shape: lin-rect, label: "仿真测试数据生成Agent" }
    FAKE_DATA_SAMPLE:::DBClass@{shape: rect, label: "仿真测试数据集"}
    FAKE_DATA_DB:::DBClass@{shape: lin-cyl, label: "仿真测试数据存储库"}
    FAKER_FACTORY_SERVER:::OutServerClass@{shape: tag-rect, label: "仿真数据生成服务\n身份证、手机号、地市编码" }
    UDF_CHECKER:::OutServerClass@{shape: tag-rect, label: "udf函数执行服务" }
    DATA_META_DOCS:::OutServerClass@{ shape: tag-rect, label: "数仓知识库服务\n(表结构和治理任务SQL)" }
    TABLE_COL_INFO:::metaClass@{shape: lin-doc, label: "表字段信息" }
    JOB_SQL_INFO:::metaClass@{shape: lin-doc, label: "治理SQL信息" }
    SQL_PARSER:::OutServerClass@{ shape: tag-rect, label: "SQL解析服务" }
    SQL_CONDITION:::metaClass@{shape: rect, label: "where条件
    join条件
    udf函数字段
    ……"}
    LANGUFSE:::LangFuseClass@{ shape: tag-rect, label: "LangFuse监测感知评估" }
    OUTPUT_SERVER:::DBClass@{ shape: tag-rect, label: "数据输出器" }
    CHECKER_AGENT:::agentClass@{ shape: lin-rect, label: "仿真数据校验Agent" }


    START --> INPUT_TABLE
    START -.-> INPUT_SQL --> SQL_PARSER
    INPUT_TABLE --> DATA_META_DOCS
    DATA_META_DOCS --> TABLE_COL_INFO & JOB_SQL_INFO
    JOB_SQL_INFO --> SQL_PARSER --> SQL_CONDITION

    PARSE_COL_PROMPT_TEMPLATE & TABLE_COL_INFO --> PARSE_COL_PROMPT --> PARSE_COL_AGNET
    PARSE_COL_AGNET <--> LLMS & FAKER_FACTORY_SERVER
    PARSE_COL_AGNET --> SAMPLE_DATA

    SQL_CONDITION & JOB_SQL_INFO & TABLE_COL_INFO & GEN_PROMPT_TEMPLATE --> GEN_PROMPT --> GEN_FAKE_DATA_AGENT
    SAMPLE_DATA --> GEN_FAKE_DATA_AGENT
    GEN_FAKE_DATA_AGENT <--> LLMS
    GEN_FAKE_DATA_AGENT --> FAKE_DATA_SAMPLE


    CHECKER__PROMPT_TEMPLATE:::templateClass@{ shape: doc, label: "数据校验提示词模板"}
    CHECKER__PROMPT:::promptClass@{ shape: odd, label: "数据校验提示词" }
    CHECKER__PROMPT_TEMPLATE & SQL_CONDITION & JOB_SQL_INFO & TABLE_COL_INFO --> CHECKER__PROMPT
    FAKE_DATA_SAMPLE & CHECKER__PROMPT --> CHECKER_AGENT <-->|校验生成的数据是否满足udf where条件| UDF_CHECKER
    CHECKER_AGENT <--> LLMS
    CHECKER_AGENT -->|校验通过入库存储| FAKE_DATA_DB

    CHECKER_AGENT -.->|校验不通过时给出修改建议| GEN_FAKE_DATA_AGENT & PARSE_COL_AGNET

    FAKE_DATA_DB --> OUTPUT_SERVER --> END

    GEN_FAKE_DATA_AGENT & CHECKER_AGENT & PARSE_COL_AGNET -.-> LANGUFSE

    classDef agentClass fill:#f9f,font-weight:bold;
    classDef importantClass fill:#6ED391FF,font-weight:bold;
    classDef templateClass fill:#BEE6888F,font-weight:bold;
    classDef promptClass fill:#83D70E8F,font-weight:bold;
    classDef OutServerClass fill:#6CC9E6B8,font-weight:bold;
    classDef LLMClass fill:#E8D38180,font-weight:bold;
    classDef metaClass fill:#E8818180,font-weight:bold;
    classDef DBClass fill:#BB81E880,font-weight:bold;
    classDef LangFuseClass fill:#003BFE57,font-weight:bold;
    classDef UserInputClass fill:#DAD65E8A,font-weight:bold;
```

```mermaid
---
title: DataForge - AI仿真数据生成工具
config:
  look: handDrawn
  theme: normal
  layout: elk
  elk:
    mergeEdges: false
    nodePlacementStrategy: LINEAR_SEGMENTS
---
flowchart TD
    START@{shape: circle, label: "start"}
    END@{shape: circle, label: "END"}
    A@{ shape: braces, label: "1、数仓表结构信息\n2、数仓数据治理任务SQL" }
    B@{shape: braces, label: "身份证、手机号、地市编码等" }
    C@{shape: manual-input, label: "业务查询SQL" }
    D@{shape: manual-input, label: "期望生成表名称"}
    E@{ shape: braces, label: "表where条件、join条件等信息" }
    F(提示词模板)
    G1@{ shape: odd, label: "仿真数据生成提示词" }
    G[[提示词生成器]]
    H@{shape: procs, label: LLM服务}
    I:::pinkClass@{ shape: rect, label: "数据生成Agent
    (使用LangGraph实现)" }
    J[MCP-仿真数据生成服务]
    K[MCP-数仓知识库]
    L[MCP-UDF函数执行服务]
    O[MCP-SQL解析服务]
    M@{shape: lin-cyl, label: "仿真数据"}
    N[[数据输出器]]
    P["LangFuse
    监测感知评估"]
    R@{shape: braces, label: "执行udf函数输出结果" }

    START --> C & D
    C -.-> G
    D --> G
    subgraph DataForge
    F --> G
    G --> G1 --> I
    end

    subgraph "MCP服务矩阵"
    I <-.-> J & K & L & O & K
    K --> A
    O --> E
    L --> R
    J --> B
    end

    subgraph "输出数据"
    I --> M --> N --> END
    end

    I <--> H
    I -.-> P

    classDef pinkClass fill:#f9f,font-weight:bold;
    classDef importantClass fill:#eb6d6f,font-weight:bold;
```

## 项目概述
本项目是一个基于数据仓库元数据信息自动生成仿真数据的工具，支持两种表类型：
- ODS(原始数据表)：外部系统接入的原始数据
- ADM(知识库表)：经过治理任务处理的业务数据

通过LLM（大语言模型）技术根据表定义生成符合业务逻辑的测试数据，并保持表间关联关系，为开发和测试提供高质量的数据支持。

## 核心功能
- **元数据驱动**：解析数据仓库的表定义信息（字段名、类型、约束等）
- **智能数据生成**：利用LLM根据字段语义生成合理的仿真数据
- **关联数据构建**：根据表的血缘关系保持数据间的业务逻辑一致性
- **测试支持**：生成的数据可直接用于单元测试、集成测试和开发自测

## 技术特点
1. 采用Python作为主要开发语言
2. 集成大语言模型API进行智能数据生成
3. 支持多种数据源元数据解析
4. 可配置的数据生成规则和关联策略
5. 提供命令行和API两种使用方式
6. 使用uv进行高效的Python依赖管理

## 使用场景
- 开发环境数据准备
- 自动化测试数据生成
- 数据可视化演示
- 系统性能测试

## 快速开始

### 前置条件
- 已安装Python 3.10+
- 已安装uv (可通过`pip install uv`安装)

### 安装与运行
```bash
# 安装项目依赖
uv pip install -e .

# 或开发模式安装(包含测试依赖)
uv pip install -e ".[dev]"

# 运行数据生成
python main.py --metadata /path/to/metadata.json --output /path/to/output
```

### 常用uv命令
```bash
# 更新所有依赖
uv pip install --upgrade -r requirements.txt

# 检查依赖冲突
uv pip check

# 导出依赖列表
uv pip freeze > requirements.txt
```

## 配置说明
在pyproject.toml中配置：
- LLM API密钥
- 数据生成规则
- 关联关系策略
- 输出格式选项


## prompt demo

```
数据库表名称:
fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE
期望条件：
fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE:
1. CERTIFICATE_CODE is not null AND MSISDN like '139%' and AGE <100 and SEXCODE is not null
2. CERTIFICATE_CODE身份证号码要和AGE年龄、SEXCODE性别逻辑匹配
期望生成数据条数:
fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE: 5
```


```
数据库表名称:
fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE
期望生成数据条数:
fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE: 5
```