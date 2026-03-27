# API 文档

## 概述

本文档描述航空公司产品智能体系统的所有API接口。

---

## 1. 产品查询接口

### 1.1 search_airline_products

**描述**: 搜索包含关键词的航空公司产品

**参数**:
- `keyword` (string): 搜索关键词，可以是产品名称、航线、备注等

**返回**: 匹配的产品列表（JSON格式）

**示例**:
```python
search_airline_products("经济舱")
```

---

### 1.2 get_products_by_airline

**描述**: 根据航空公司代码查询产品

**参数**:
- `airline_code` (string): 航空公司代码（如：MU, CZ, HU, CA等）

**返回**: 该航空公司的所有产品列表

**示例**:
```python
get_products_by_airline("MU")
```

---

## 2. 统计信息接口

### 2.1 get_all_airlines

**描述**: 获取所有航空公司列表

**参数**: 无

**返回**: 所有航空公司代码列表

**示例**:
```python
get_all_airlines()
```

---

### 2.2 get_agent_statistics

**描述**: 获取智能体统计信息

**参数**: 无

**返回**: 统计信息（产品总数、航空公司数量、航线数量等）

**示例**:
```python
get_agent_statistics()
```

---

## 3. 文档帮助接口

### 3.1 get_documentation_help

**描述**: 获取文档帮助信息

**参数**:
- `topic` (string, 可选): 帮助主题，不提供则返回总体帮助

**返回**: 帮助信息内容

**示例**:
```python
get_documentation_help("查询")
```

---

## 4. 数据导出接口

### 4.1 export_products_to_excel

**描述**: 导出所有产品数据到Excel文件

**参数**: 无

**返回**: 导出结果和文件路径

**示例**:
```python
export_products_to_excel()
```

---

## 数据结构

### 产品对象 (AirlineProduct)

```json
{
  "airline": "MU",
  "product_name": "1、里程优享 - 所有航线",
  "route": "所有航线",
  "booking_class": "Y",
  "price_increase": 0,
  "rebate_ratio": "",
  "office": "",
  "remarks": "所有GP优享产品可适用于航前4小时免费改期的政策",
  "valid_period": "2026年"
}
```

### 统计信息 (Statistics)

```json
{
  "total_products": 150,
  "total_airlines": 8,
  "total_routes": 50,
  "products_by_airline": {
    "MU": 25,
    "CZ": 30,
    "HU": 20,
    "CA": 35,
    ...
  }
}
```

---

## 错误处理

所有API在出错时会返回包含错误信息的JSON对象：

```json
{
  "message": "错误描述",
  "error": "错误详情"
}
```

常见错误码：
- 未找到数据
- 参数错误
- 文件读写错误
