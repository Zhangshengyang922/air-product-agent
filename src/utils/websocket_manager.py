"""
WebSocket管理模块
实现前后端实时通信
"""

import json
import time
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储所有活跃的WebSocket连接
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """接受新的WebSocket连接"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"新的WebSocket连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """向特定客户端发送消息"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        message_str = json.dumps(message, ensure_ascii=False)

        # 复制连接列表，避免在迭代时修改
        connections = list(self.active_connections)

        for connection in connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                self.disconnect(connection)

        logger.info(f"广播消息成功: {message.get('type', 'unknown')}, 接收者: {len(connections)}")

    def get_connection_count(self):
        """获取当前连接数"""
        return len(self.active_connections)


# 全局连接管理器实例
manager = ConnectionManager()


# 消息类型常量
class MessageType:
    """WebSocket消息类型"""

    DATA_UPDATED = "data_updated"  # 数据更新
    FILE_CHANGED = "file_changed"  # 文件变化
    HEARTBEAT = "heartbeat"  # 心跳


async def notify_data_updated(reason="数据已更新"):
    """
    通知所有客户端数据已更新

    Args:
        reason: 更新原因
    """
    message = {
        "type": MessageType.DATA_UPDATED,
        "data": {
            "reason": reason,
            "timestamp": int(time.time())
        }
    }
    await manager.broadcast(message)


async def notify_file_changed(file_path: str):
    """
    通知所有客户端文件已变化

    Args:
        file_path: 变化的文件路径
    """
    message = {
        "type": MessageType.FILE_CHANGED,
        "data": {
            "file_path": file_path,
            "timestamp": int(time.time())
        }
    }
    await manager.broadcast(message)
