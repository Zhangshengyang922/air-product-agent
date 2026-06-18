# -*- coding: utf-8 -*-
import re
import pandas as pd
import sys

# 手动解析CSV文件
csv_file = r'C:/Users/Administrator/OneDrive/桌面/各航司汇总产品.csv'

print("开始解析CSV文件...")

# 读取原始内容
try:
    with open(csv_file, 'rb') as f:
        content = f.read()

    # 尝试不同编码解码
    for encoding in ['utf-8', 'gbk', 'gb18030']:
        try:
            text = content.decode(encoding)
            print(f"成功用 {encoding} 解码")
            break
        except:
            continue
    else:
        # 尝试忽略错误
        text = content.decode('utf-8', errors='ignore')
        print("使用 utf-8 (忽略错误) 解码")

    # 逐行解析
    lines = text.split('\n')
    products = []

    # CSV列名
    headers = ['airline', 'product_name', 'route', 'booking_class', 'price_increase', 'rebate_ratio', 'office', 'remarks', 'valid_period', 'ticket_type', 'policy_identifier', 'policy_code']

    # 解析每一行
    current_product = {}
    field_index = 0

    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue

        # 检查是否是新产品（航司代码开头）
        airline_match = re.match(r'^([A-Z0-9]+)\s*,', line)

        if airline_match:
            # 保存上一个产品
            if current_product:
                products.append(current_product.copy())

            # 开始新产品
            current_product = {'airline': airline_match.group(1)}
            rest = line[airline_match.end():]

            # 解析剩余字段
            fields = []
            current_field = ''
            in_quotes = False

            for char in rest:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    fields.append(current_field.strip())
                    current_field = ''
                else:
                    current_field += char
            fields.append(current_field.strip())

            # 填充字段
            for i, field in enumerate(fields):
                col_name = headers[i + 1] if i + 1 < len(headers) else f'field_{i+1}'
                current_product[col_name] = field

        else:
            # 继续添加到remarks字段
            if 'remarks' in current_product:
                current_product['remarks'] = current_product['remarks'] + '\n' + line.strip()
            else:
                current_product['remarks'] = line.strip()

    # 保存最后一个产品
    if current_product:
        products.append(current_product)

    print(f"\n解析完成，共 {len(products)} 个产品")

    # 转换为DataFrame
    df = pd.DataFrame(products)

    # 确保所有列都存在
    for col in headers:
        if col not in df.columns:
            df[col] = ''

    # 只保留有数据的列
    df = df[[col for col in headers if col in df.columns or col == 'airline']]

    # 保存为标准CSV
    output_file = r'c:/Users/Administrator/OneDrive/桌面/air_prd_agent/assets/new_products_parsed.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"已保存到: {output_file}")

    # 显示统计信息
    print("\n各航司产品数量:")
    print(df['airline'].value_counts())

    # 显示前5个产品
    print("\n前5个产品:")
    print(df.head().to_string())

except Exception as e:
    print(f"发生错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
