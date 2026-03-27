# 产品管理系统 - 快速操作指南

## 🚀 快速开始

### 1. 启动服务

**方式A：双击运行**
```
start_server.bat
```

**方式B：命令行**
```bash
cd "C:\Users\Administrator\OneDrive\桌面\air_prd_agent"
python src\main.py -m http -p 8000
```

### 2. 访问系统

- **本地访问**：http://localhost:8000
- **局域网访问**：http://本机IP:8000
- **登录账号**：YNTB / yntb123

---

## 📊 更新产品数据

### 方式1：Excel导入（推荐）

1. **准备文件**
   - 将Excel文件放到项目根目录
   - 命名：`exported_from_wechat.xlsx`

2. **导入数据**
   ```bash
   python final_import.py
   ```
   或双击运行 `update_products.bat`

3. **查看结果**
   - 脚本会显示导入统计
   - 访问Web页面验证

### 方式2：直接替换CSV

```bash
# 复制新文件替换
copy 新产品.csv assets\products.csv
```

系统会自动重载，无需重启。

### 方式3：Web界面上传

1. 访问 http://localhost:8000
2. 登录后点击"上传产品"
3. 选择文件并导入

---

## 🌐 局域网访问

### 步骤1：获取本机IP

```bash
ipconfig
```

找到IPv4地址，例如：`192.168.1.100`

### 步骤2：访问

在同一局域网的其他电脑访问：
```
http://192.168.1.100:8000
```

### 步骤3：配置防火墙

确保Windows防火墙放行8000端口。

---

## ⚡ 开机自启动

### 创建启动任务

1. **Win+R** → 输入 `taskschd.msc`
2. 点击"创建基本任务"
3. 名称：`产品管理系统`
4. 触发器：计算机启动时
5. 操作：启动程序
   - 程序：`python.exe` 完整路径
   - 参数：`"C:\Users\Administrator\OneDrive\桌面\air_prd_agent\src\main.py" -m http -p 8000`
   - 起始于：`C:\Users\Administrator\OneDrive\桌面\air_prd_agent`

---

## 🔧 常用命令

```bash
# 启动服务
python src\main.py -m http -p 8000

# 导入产品
python final_import.py

# 检查端口
netstat -ano | findstr :8000

# 结束进程
taskkill /F /IM python.exe

# 查看日志
type server.log

# 检查IP
ipconfig
```

---

## 📂 文件说明

| 文件 | 说明 |
|------|------|
| `start_server.bat` | 启动服务快捷方式 |
| `update_products.bat` | 更新产品数据快捷方式 |
| `final_import.py` | Excel导入脚本 |
| `assets/products.csv` | 产品数据文件 |
| `操作指南.md` | 详细操作手册 |

---

## ❓ 常见问题

### Q: 端口8000被占用？
**A:** 结束占用进程或更换端口：
```bash
taskkill /F /IM python.exe
python src\main.py -m http -p 9000
```

### Q: 局域网无法访问？
**A:**
1. 检查防火墙设置
2. 确认IP地址正确
3. 确保在同一局域网

### Q: 数据更新不生效？
**A:**
1. 刷新浏览器（Ctrl+F5）
2. 重启服务
3. 检查文件编码（UTF-8）

### Q: 导入失败？
**A:**
1. 确认文件名：`exported_from_wechat.xlsx`
2. 检查Excel格式
3. 查看错误信息

---

## 📞 技术支持

- **服务端口**：8000
- **登录账号**：YNTB / yntb123
- **数据文件**：assets/products.csv
- **日志文件**：server.log

---

**版本**：v1.0
**更新日期**：2026-03-25
