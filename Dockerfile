FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用文件
COPY main.py .
COPY assets/ ./assets/
COPY static/ ./static/
COPY src/ ./src/
COPY config/ ./config/
COPY "26年大客户汇总表-国航.csv" .
COPY "26年大客户汇总表-川航.csv" .
COPY "26年大客户汇总表-南航.csv" .
COPY 各航司汇总产品-KY.csv .

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
