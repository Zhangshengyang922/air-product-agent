#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复Excel文件样式问题
将Excel文件另存为新的文件，去除有问题的样式
"""

import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_excel_file(input_file: Path, output_file: Path):
    """
    修复Excel文件

    使用 openpyxl 重新保存文件来去除有问题的样式
    """
    try:
        import openpyxl

        logger.info(f"开始修复Excel文件: {input_file}")

        # 尝试加载工作簿
        wb = openpyxl.load_workbook(input_file, data_only=True)

        # 保存到新文件
        wb.save(output_file)
        wb.close()

        logger.info(f"修复成功，保存到: {output_file}")
        return True

    except Exception as e:
        logger.error(f"修复失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    input_file = Path(r"C:\Users\Administrator\OneDrive\桌面\各航司汇总产品.xlsx")
    output_file = Path(r"C:\Users\Administrator\OneDrive\桌面\各航司汇总产品_fixed.xlsx")

    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    print(f"输入文件存在: {input_file.exists()}")

    if not input_file.exists():
        print("[ERROR] 输入文件不存在")
        return

    # 备份原文件
    backup_file = Path(str(input_file) + ".bak")
    shutil.copy(input_file, backup_file)
    print(f"[OK] 已备份原文件到: {backup_file}")

    # 尝试修复
    if fix_excel_file(input_file, output_file):
        print("[OK] Excel文件修复成功")
        print(f"[INFO] 新文件已保存到: {output_file}")
        print(f"[TIP] 请使用修复后的文件 {output_file} 进行数据更新")
    else:
        print("[ERROR] Excel文件修复失败")
        print("[TIP] 建议：请手动将Excel文件另存为CSV格式")


if __name__ == "__main__":
    main()
