#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""获取本机IP地址"""

import socket
import platform

def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

if __name__ == '__main__':
    print('='*60)
    print('本机IP地址')
    print('='*60)
    print()

    ip = get_local_ip()
    print(f'IP地址: {ip}')
    print()

    print('访问地址:')
    print(f'  本地访问:   http://localhost:8000')
    print(f'  127.0.0.1:   http://127.0.0.1:8000')
    print(f'  局域网访问: http://{ip}:8000')
    print(f'  本机访问:   http://{ip}:8000')
    print()

    print('登录信息:')
    print('  用户名: YNTB')
    print('  密码: yntb123')
    print()

    print('='*60)
