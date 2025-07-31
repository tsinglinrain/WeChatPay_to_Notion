FROM python:3.13.5-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制requirements文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建用于存储数据的目录
RUN mkdir -p /app/attachment /app/bill_csv_raw

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 暴露端口（如果需要的话）
# EXPOSE 8000

# 默认命令
CMD ["python", "main.py"]
