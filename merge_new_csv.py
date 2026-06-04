#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
合并 csv_updates/ 下所有"产品汇总新格式5.28-*.csv" 为统一的 products.csv
"""
import os
import pandas as pd
from pathlib import Path

project_root = Path(__file__).parent
csv_dir = project_root / "csv_updates"
output_path = project_root / "assets" / "products.csv"

# 航司代码到名称的映射（从 main.py AIRLINE_NAMES 和文件名提取）
AIRLINE_NAMES = {
    "3U": "四川航空", "8L": "祥鹏航空", "9H": "长安航空", "A6": "湖南航空",
    "BK": "奥凯航空", "CA": "中国国航", "CZ": "南方航空", "DR": "瑞丽航空",
    "DZ": "东海航空", "EU": "成都航空", "FU": "福州航空", "G5": "华夏航空",
    "GJ": "长龙航空", "GS": "天津航空", "GX": "北部湾航空", "HU": "海南航空",
    "JD": "首都航空", "JR": "幸福航空", "KY": "昆明航空", "MF": "厦门航空",
    "MU": "东方航空", "NS": "河北航空", "PN": "西部航空", "QW": "青岛航空",
    "RY": "江西航空", "SC": "山东航空", "TV": "西藏航空", "UQ": "乌鲁木齐航空",
    "ZH": "深圳航空",
}

all_data = []
file_count = 0

for file in sorted(csv_dir.glob("产品汇总新格式5.28-*.csv")):
    print(f"[读取] {file.name}")
    try:
        df = pd.read_csv(file, encoding='utf-8-sig')
        df = df.fillna('')
        
        # 清理列名：去除多余空格和空列
        df.columns = [col.strip() for col in df.columns]
        # 移除完全为空的列
        df = df.dropna(axis=1, how='all')
        # 移除无名列
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 统一列名：有些文件用"有效及截止日期"，需拆分为开始/结束
        if '有效及截止日期' in df.columns and '有效开始日期' not in df.columns:
            # 拆分为开始和结束日期
            def split_date(val):
                s = str(val).strip().replace('：', ':')
                if '-' in s or '至' in s:
                    sep = '-' if '-' in s else '至'
                    parts = s.split(sep, 1)
                    return pd.Series([parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''])
                return pd.Series([s, ''])
            df[['有效开始日期', '有效截止日期']] = df['有效及截止日期'].apply(split_date)
            df = df.drop(columns=['有效及截止日期'])
        
        # 从文件名提取航司代码，如 "产品汇总新格式5.28-3U川航.csv" -> "3U"
        fname = file.stem
        parts = fname.split('-')
        if len(parts) >= 2:
            code_part = parts[-1]  # e.g., "3U川航"
            # 提取大写字母+数字作为航司代码（停在中文字符前）
            airline_code = ""
            for ch in code_part:
                if ch.isupper() or ch.isdigit():
                    airline_code += ch
                else:
                    break
        
        # 确保"航司"列有标准代码（不含中文）
        if '航司' in df.columns:
            # 清理航司列 - 移除中文字符，只保留代码
            def clean_code(val):
                s = str(val).strip()
                if not s:
                    return airline_code
                # 去除中文字符
                code = ""
                for ch in s:
                    if ch.isupper() or ch.isdigit():
                        code += ch
                    elif '\u4e00' <= ch <= '\u9fff':
                        break  # 遇到中文停止
                return code if code else airline_code
            df['航司'] = df['航司'].apply(clean_code)
        
        all_data.append(df)
        file_count += 1
        print(f"  -> {len(df)} 行")
    except Exception as e:
        print(f"  [错误] {e}")

if not all_data:
    print("没有找到任何新格式CSV文件！")
    exit(1)

# 合并
merged = pd.concat(all_data, ignore_index=True)

# 清理：移除空行和说明行
merged = merged.dropna(subset=['产品名称'] if '产品名称' in merged.columns else ['航线'])
merged = merged[merged['产品名称'].astype(str).str.strip() != '']

# 添加航司名称列（补充缺失的列）
if '航司名称' not in merged.columns:
    merged['航司名称'] = merged['航司'].map(AIRLINE_NAMES).fillna('')

# 统一输出列顺序（新旧兼容）
output_columns = [
    '航司', '航司名称', '产品名称', '航线', '订座舱位', '上浮价格',
    '前返计算方式', '前返计算值', '后返计算方式', '后返计算值', '定额代理费',
    '运价标识', '票证类型', '出票OFFICE', '备注',
    '有效开始日期', '有效截止日期', '创建人', '创建时间'
]

# 确保所有输出列存在
for col in output_columns:
    if col not in merged.columns:
        merged[col] = ''

merged = merged[output_columns]

# 保存
merged.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n[完成] 合并 {file_count} 个文件，共 {len(merged)} 行数据")
print(f"[输出] {output_path}")
print(f"[列名] {list(merged.columns)}")
print(f"[航司] {sorted(merged['航司'].unique())}")
