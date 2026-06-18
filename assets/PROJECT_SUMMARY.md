# 项目总结

## 项目概述

本项目是一个**航空公司产品智能体系统**，集成了产品管理和文档查询功能。

---

## 核心功能

### 1. 产品管理
- 产品数据导入与清洗
- 产品查询与搜索
- 产品统计分析
- 产品数据导出

### 2. 文档系统
- 文档加载与管理
- 文档搜索与检索
- 帮助信息查询

### 3. 智能体功能
- 自然语言交互
- 工具调用与执行
- 短期记忆管理

---

## 技术架构

### 前端
- LangChain Agent框架
- 自然语言处理
- 对话管理

### 后端
- Python数据管理
- Pandas数据处理
- Excel文件导出

### 数据存储
- CSV文件存储
- Markdown文档存储

---

## 项目结构

```
/workspace/projects/
├── config/
│   └── agent_llm_config.json      # 智能体配置
├── src/
│   ├── agents/
│   │   └── agent.py                # 智能体主程序
│   ├── storage/
│   │   └── memory/
│   │       └── memory_saver.py     # 记忆管理
│   └── tools/                      # 工具定义
└── assets/
    ├── cleaned_data/               # 清洗后的数据
    ├── docs/                       # 文档目录
    └── agent_data_with_docs/       # 导出数据
```

---

## 数据模型

### 航空公司产品 (AirlineProduct)

包含以下字段：
- `airline`: 航空公司代码
- `product_name`: 产品名称
- `route`: 航线
- `booking_class`: 订座舱位
- `price_increase`: 上浮价格
- `rebate_ratio`: 返比例/做单
- `office`: 出票OFFICE
- `remarks`: 备注
- `valid_period`: 产品有效期

---

## 可用工具

1. **search_airline_products**: 搜索产品
2. **get_products_by_airline**: 按航空公司查询
3. **get_all_airlines**: 获取所有航空公司
4. **get_agent_statistics**: 获取统计信息
5. **get_documentation_help**: 获取帮助
6. **export_products_to_excel**: 导出数据

---

## 配置说明

智能体配置文件 `config/agent_llm_config.json` 包含：

- **模型配置**: 使用的LLM模型和参数
- **系统提示词**: 智能体的角色和行为定义
- **工具列表**: 可用的工具函数

---

## 部署说明

### 环境要求
- Python 3.8+
- pandas
- openpyxl
- langchain
- langgraph
- coze-coding-dev-sdk

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行
```bash
python src/main.py
```

---

## 扩展计划

1. 支持更多航空公司数据
2. 增加实时价格查询
3. 集成航班时刻表
4. 支持在线订票功能
5. 增加用户反馈系统

---

## 贡献者

- Vibe Coding Team

---

## 许可证

MIT License
