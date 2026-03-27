import pandas as pd
import json
from pathlib import Path

# 字段映射
FIELD_MAPPING = {
    '航司代码': 'airline',
    '航司名称': 'airline_name',
    '产品名称': 'product_name',
    '航线': 'route',
    '订座舱位': 'booking_class',
    '上浮价格': 'price_increase',
    '政策返点': 'rebate_ratio',
    '产品代码': 'policy_code',
    '出票OFFICE': 'office',
    '备注': 'remarks',
    '产品有限期': 'valid_period'
}

def clean_value(val):
    """清理数据值"""
    if pd.isna(val) or val == 'NaN' or val == 'nan':
        return ''
    return str(val).strip()

def clean_price(val):
    """清理价格数据"""
    if pd.isna(val) or val == 'NaN' or val == 'nan':
        return 0
    # 提取数字
    import re
    match = re.search(r'(\d+)', str(val))
    if match:
        return int(match.group(1))
    return 0

def import_csv_data(csv_path, output_path):
    """导入CSV数据并转换为标准格式"""
    df = pd.read_csv(csv_path, encoding='utf-8')

    # 重命名列
    df = df.rename(columns=FIELD_MAPPING)

    # 确保所有必需列存在
    required_cols = ['product_id', 'airline', 'product_name', 'route', 'booking_class',
                   'price_increase', 'rebate_ratio', 'policy_code', 'office',
                   'remarks', 'valid_period', 'ticket_type', 'policy_identifier']

    for col in required_cols:
        if col not in df.columns:
            df[col] = ''

    # 添加product_id
    import uuid
    df['product_id'] = df.apply(lambda x: str(uuid.uuid4()).replace('-', '')[:16], axis=1)

    # 清理数据
    df['price_increase'] = df['price_increase'].apply(clean_price)
    df['rebate_ratio'] = df['rebate_ratio'].apply(clean_price)
    df['remarks'] = df['remarks'].apply(clean_value)
    df['office'] = df['office'].apply(clean_value)
    df['valid_period'] = df['valid_period'].apply(clean_value)
    df['policy_code'] = df['policy_code'].apply(clean_value)
    df['ticket_type'] = 'ALL'
    df['policy_identifier'] = ''

    # 选择并排序列
    df = df[required_cols]

    # 保存
    df.to_json(output_path, orient='records', force_ascii=False)
    print(f'成功导入 {len(df)} 条产品数据到 {output_path}')

    return df

if __name__ == '__main__':
    csv_path = 'assets/products.csv'
    output_path = 'assets/products.json'

    df = import_csv_data(csv_path, output_path)

    print('\n数据统计:')
    print(f'- 总产品数: {len(df)}')
    print(f'- 航司数量: {df["airline"].nunique()}')
    print(f'\n航司分布:')
    print(df['airline'].value_counts().to_string())
