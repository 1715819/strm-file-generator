FROM python:3.9-slim

# 保持默认root用户
WORKDIR /app

# 安装依赖
RUN apt-get update && apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# 复制文件
COPY bot/requirements.txt .
COPY bot/main.py .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建目录并修复权限
RUN mkdir -p /app/alist && \
    chmod 777 /app/alist  # 关键步骤

CMD ["python", "main.py"]
