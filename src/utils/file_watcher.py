"""
文件监控模块
监控CSV文件变化并自动刷新产品数据
"""

import os
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ProductFileHandler(FileSystemEventHandler):
    """产品文件变化处理器"""

    def __init__(self, file_path, on_change_callback):
        """
        初始化文件处理器

        Args:
            file_path: 监控的文件路径
            on_change_callback: 文件变化时的回调函数
        """
        self.file_path = Path(file_path).resolve()
        self.on_change_callback = on_change_callback
        self.last_modified = 0

    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return

        event_path = Path(event.src_path).resolve()

        # 只处理我们监控的文件
        if event_path == self.file_path:
            # 避免频繁触发（同一个修改事件可能触发多次）
            current_modified = event_path.stat().st_mtime
            if current_modified - self.last_modified < 2:  # 2秒内的重复修改忽略
                return

            self.last_modified = current_modified
            logger.info(f"检测到文件变化: {self.file_path}")

            # 等待文件写入完成
            time.sleep(0.5)

            # 执行回调函数
            if self.on_change_callback:
                try:
                    self.on_change_callback(self.file_path)
                except Exception as e:
                    logger.error(f"文件变化回调执行失败: {e}", exc_info=True)


class FileWatcher:
    """文件监控器"""

    def __init__(self, file_path, on_change_callback=None):
        """
        初始化文件监控器

        Args:
            file_path: 监控的文件路径
            on_change_callback: 文件变化时的回调函数
        """
        self.file_path = Path(file_path)
        self.observer = Observer()

        # 创建事件处理器
        self.handler = ProductFileHandler(
            file_path=self.file_path,
            on_change_callback=on_change_callback
        )

    def start(self):
        """启动文件监控"""
        if not self.file_path.exists():
            logger.warning(f"监控文件不存在: {self.file_path}")
            return False

        try:
            # 监控文件所在目录
            watch_dir = str(self.file_path.parent)
            self.observer.schedule(self.handler, watch_dir, recursive=False)
            self.observer.start()
            logger.info(f"文件监控已启动: {self.file_path}")
            return True
        except Exception as e:
            logger.error(f"启动文件监控失败: {e}", exc_info=True)
            return False

    def stop(self):
        """停止文件监控"""
        try:
            self.observer.stop()
            self.observer.join()
            logger.info("文件监控已停止")
        except Exception as e:
            logger.error(f"停止文件监控失败: {e}", exc_info=True)

    def is_running(self):
        """检查监控是否在运行"""
        return self.observer.is_alive()


# 全局文件监控器实例
_file_watcher = None


def start_file_watcher(file_path, on_change_callback=None):
    """
    启动文件监控器（全局单例）

    Args:
        file_path: 监控的文件路径
        on_change_callback: 文件变化时的回调函数

    Returns:
        FileWatcher: 文件监控器实例
    """
    global _file_watcher

    # 如果已有监控器在运行，先停止
    if _file_watcher and _file_watcher.is_running():
        _file_watcher.stop()

    # 创建新的监控器
    _file_watcher = FileWatcher(file_path, on_change_callback)
    _file_watcher.start()

    return _file_watcher


def stop_file_watcher():
    """停止文件监控器（全局单例）"""
    global _file_watcher

    if _file_watcher:
        _file_watcher.stop()
        _file_watcher = None
