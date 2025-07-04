# ----- 知识点 -----
# （Docker >= 17.05）
# BuildKit 构建器：会自动优化相邻的相同指令
# 多行和单行效果相同：都只创建一个层
# 镜像大小基本无差异


# 多阶段构建 Dockerfile
# 第一阶段：构建依赖
FROM python:3.13-slim-bookworm AS builder


# 设置工作目录
WORKDIR /app

# 安装系统依赖（构建时需要）
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv 包管理器（比 pip 更快）
RUN pip install --no-cache-dir uv

# 复制项目配置文件
COPY pyproject.toml ./
COPY uv.lock ./

# 使用 uv 创建虚拟环境并安装依赖
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 配置 uv 使用阿里云镜像源并安装依赖
RUN uv pip install --no-cache-dir -r pyproject.toml

# 第二阶段：运行时镜像
FROM python:3.13-slim-bookworm AS runtime

# 创建非 root 用户
RUN groupadd -r gmx && useradd -r -g gmx gmx

# 安装运行时系统依赖
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
# 禁用 Python 的输出缓冲
ENV PYTHONUNBUFFERED=1
# 阻止 Python 生成 .pyc 字节码文件
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY pyproject.toml ./
COPY .python-version ./

# 更改文件所有者
RUN chown -R gmx:gmx /app

# 切换到非 root 用户
USER gmx

