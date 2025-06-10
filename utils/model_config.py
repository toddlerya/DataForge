#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/3/7 13:57
# @Author   : guoqun X2590
# @FileName : model_config.py
# @Project  : LLM4Tester


class ModelServerSchema:
    base_url: str
    model: str
    # 限制大模型返回的最大输出token数
    max_tokens: int = 2048
    temperature: float = 1
    # top_p: 采样温度的替代方案，模型会考虑前top_p概率的token的结果。
    # 0.1意味着只有包括在最高10%概率中的token会被考虑，不建议与temperature同时修改
    top_p: float = 1.0
    auth_key: str

    def to_dict(self):
        """
        将 ModelServerSchema 实例转换为字典
        :return: 包含实例属性的字典
        """
        return {
            "base_url": self.base_url,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "auth_key": self.auth_key,
        }


class Test_DeepSeek_R1_Distill_Qwen_14B_AWQ(ModelServerSchema):
    """
    测试部DeepSeek-R1-Distill-Qwen-14B-AWQ模型
    """

    base_url = "http://172.16.108.3:8888/v1"
    model = "DeepSeek-R1-Distill-Qwen-14B-AWQ"
    max_tokens = 8192
    temperature = 0.6
    auth_key = "x2590.2025"


class Dev_Qwen2_5_14B_Instruct_AWQ(ModelServerSchema):
    """
    公研Qwen2.5-14B-Instruct-AWQ模型
    """

    base_url = "http://172.17.62.1:28000/v1"
    model = "fiberhome-chat"
    temperature = 0.7
    auth_key = "x2590.2025"


class Dev_DeepSeek_R1_Distill_Qwen_32B(ModelServerSchema):
    """
    公研DeepSeek-R1-Distill-Qwen-32B模型
    """

    base_url = "http://27.1.31.142:29090/v1"
    model = "DeepSeek-R1-Distill-Qwen-32B"
    temperature = 0.7
    auth_key = "x2590.2025"


class Plan_Qwen_QwQ_32B(ModelServerSchema):
    """
    规划Qwen-QWQ-32B模型
    """

    base_url = "http://172.16.111.1:11434/v1"
    model = "qwq:latest"
    temperature = 0.6
    top_p = 0.95
    auth_key = "x2590.2025"


class Plan_Qwen2_5_Coder_32B(ModelServerSchema):
    base_url = "http://172.16.111.1:11434/v1"
    model = "qwen2.5-coder:32b"
    temperature = 0.3
    top_p = 0.95
    auth_key = "x2590.2025"


class Test_QWen3_4b_q4_K_M(ModelServerSchema):
    """
    测试部qwen3:4b-q8_0模型
    """

    base_url = "http://localhost:11434/v1"
    model = "qwen3:4b-q4_K_M"
    max_tokens = 8192
    temperature = 0.6
    auth_key = "x2590.2025"


class Test_QWen3_8b_q4_K_M(ModelServerSchema):
    """
    测试部qwen3:8b-q4_K_M模型
    """

    base_url = "http://172.16.108.3:9999/v1"
    model = "qwen3:8b-q4_K_M"
    max_tokens = 8192
    temperature = 0.6
    auth_key = "x2590.2025"


if __name__ == "__main__":
    print(Test_DeepSeek_R1_Distill_Qwen_14B_AWQ().to_dict())
