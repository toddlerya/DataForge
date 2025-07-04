# 构建镜像
docker build -t llm_server_py313_env:1.0.0 .

# 运行容器
docker run -p 8000:8000 llm_server_py313_env:1.0.0

# 查看镜像大小
docker images llm_server_py313_env:1.0.0