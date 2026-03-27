"""
企业微信在线文档同步脚本
定期从企业微信在线文档导出数据并更新本地CSV

注意：企业微信在线文档需要通过网页手动导出或使用API（需要权限）
"""

import os
import time
import logging
import shutil
from datetime import datetime
from pathlib import Path

# 配置
PROJECT_ROOT = Path(__file__).parent
ASSETS_DIR = PROJECT_ROOT / "assets"
PRODUCTS_CSV = ASSETS_DIR / "products.csv"
EXPORTED_CSV = PROJECT_ROOT / "exported_from_wechat.csv"  # 从企业微信导出的文件

# 同步间隔（秒）
SYNC_INTERVAL = 60  # 默认1分钟检查一次

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def check_export_file():
    """检查是否有新导出的企业微信文档"""
    if not EXPORTED_CSV.exists():
        return False

    # 获取导出文件和现有文件的修改时间
    export_mtime = EXPORTED_CSV.stat().st_mtime
    current_mtime = 0

    if PRODUCTS_CSV.exists() and not PRODUCTS_CSV.is_symlink():
        # 如果是普通文件，获取修改时间
        current_mtime = PRODUCTS_CSV.stat().st_mtime
    elif PRODUCTS_CSV.is_symlink():
        # 如果是符号链接，获取目标文件的修改时间
        try:
            target = PRODUCTS_CSV.resolve()
            if target.exists():
                current_mtime = target.stat().st_mtime
        except:
            pass

    # 检查导出文件是否更新
    return export_mtime > current_mtime


def sync_exported_file():
    """将导出的文件同步到 products.csv"""
    try:
        logger.info(f"检测到新的导出文件: {EXPORTED_CSV}")

        # 备份现有文件
        if PRODUCTS_CSV.exists() and not PRODUCTS_CSV.is_symlink():
            backup_file = PRODUCTS_CSV.with_suffix('.csv.bak')
            shutil.copy2(PRODUCTS_CSV, backup_file)
            logger.info(f"已备份现有文件到: {backup_file}")

        # 删除旧的符号链接或文件
        if PRODUCTS_CSV.is_symlink() or PRODUCTS_CSV.exists():
            PRODUCTS_CSV.unlink()

        # 复制导出的文件
        shutil.copy2(EXPORTED_CSV, PRODUCTS_CSV)

        logger.info(f"✅ 文件同步成功: {EXPORTED_CSV} -> {PRODUCTS_CSV}")

        # 删除导出文件（可选）
        # EXPORTED_CSV.unlink()

        return True

    except Exception as e:
        logger.error(f"❌ 文件同步失败: {e}")
        return False


def main():
    """主循环"""
    logger.info("=" * 60)
    logger.info("🚀 企业微信在线文档同步服务已启动")
    logger.info("=" * 60)
    logger.info(f"📅 同步间隔: {SYNC_INTERVAL} 秒")
    logger.info(f"📁 导出文件位置: {EXPORTED_CSV}")
    logger.info(f"📁 目标文件位置: {PRODUCTS_CSV}")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📋 使用说明：")
    logger.info("1. 打开企业微信文档:")
    logger.info("   https://doc.weixin.qq.com/sheet/e3_AagAaAYPADkCNj1WqY0AVR2K3kGJf?scode=AAgAKQfkAAs3XlSStd")
    logger.info("2. 点击'文件' → '导出' → 选择 'CSV' 格式")
    logger.info("3. 将导出的文件保存到项目目录，命名为:")
    logger.info(f"   {EXPORTED_CSV.name}")
    logger.info("4. 系统会自动检测并同步文件")
    logger.info("=" * 60)
    logger.info("")

    sync_count = 0

    while True:
        try:
            if check_export_file():
                if sync_exported_file():
                    sync_count += 1
                    logger.info(f"📊 已完成 {sync_count} 次同步")

            # 等待下次检查
            time.sleep(SYNC_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\n👋 用户中断，停止同步服务")
            break
        except Exception as e:
            logger.error(f"⚠️ 同步过程出错: {e}")
            time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    # 确保目录存在
    ASSETS_DIR.mkdir(exist_ok=True)

    main()
