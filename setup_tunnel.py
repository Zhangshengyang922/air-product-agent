#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建本地HTTP隧道，将localhost:8000暴露到公网
"""

import socket
import urllib.request
import urllib.error
import json
import sys
import time

def check_internet():
    """检查网络连接"""
    try:
        urllib.request.urlopen('https://www.baidu.com', timeout=5)
        return True
    except:
        return False

def create_cloudflare_tunnel():
    """尝试使用Cloudflare Tunnel"""
    print("=" * 60)
    print("公网访问配置工具")
    print("=" * 60)
    
    if not check_internet():
        print("\n[ERROR] 网络连接失败，请检查网络")
        return
    
    print("\n[INFO] 尝试创建公网隧道...")
    print("[INFO] 本地服务: http://localhost:8000")
    print("\n请选择隧道方式:")
    print("1. 使用ngrok（需要先安装: https://ngrok.com/download）")
    print("2. 使用Cloudflare Tunnel（需要先安装: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation）")
    print("3. 仅查看本机IP地址（需要路由器端口映射）")
    
    choice = input("\n请输入选项 (1-3): ").strip()
    
    if choice == '1':
        print("\n使用ngrok:")
        print("1. 下载并安装: https://ngrok.com/download")
        print("2. 运行: ngrok http 8000")
        print("3. 复制ngrok提供的公网URL")
        
    elif choice == '2':
        print("\n使用Cloudflare Tunnel:")
        print("1. 下载cloudflared: https://github.com/cloudflare/cloudflared/releases")
        print("2. 运行: cloudflared tunnel --url http://localhost:8000")
        print("3. 复制cloudflared提供的公网URL")
        
    elif choice == '3':
        try:
            # 获取公网IP
            external_ip = urllib.request.urlopen('https://api.ipify.org?format=text', timeout=10).read().decode('utf-8')
            
            # 获取本机局域网IP
            local_ip = socket.gethostbyname(socket.gethostname())
            
            print("\n" + "=" * 60)
            print("IP地址信息:")
            print("=" * 60)
            print(f"公网IP: {external_ip}")
            print(f"局域网IP: {local_ip}")
            print(f"本地端口: 8000")
            
            print("\n要使公网可访问，需要:")
            print("1. 登录路由器管理页面")
            print("2. 找到'端口映射'或'虚拟服务器'设置")
            print(f"3. 添加映射: 外部端口8000 -> 内部IP:{local_ip} 端口8000")
            print("4. 配置完成后，访问: http://" + external_ip + ":8000")
            
        except Exception as e:
            print(f"\n[ERROR] 获取IP失败: {e}")
    
    else:
        print("\n无效的选项")

if __name__ == '__main__':
    create_cloudflare_tunnel()
