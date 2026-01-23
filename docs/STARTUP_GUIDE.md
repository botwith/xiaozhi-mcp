# XiaoZhi MCP 启动脚本

本项目提供了两种在 Ubuntu 上管理服务的方式：

## 方式一：Shell 脚本（推荐用于开发环境）

### 使用方法

```bash
# === 服务管理 ===

# 启动服务
./xiaozhi-mcp.sh start

# 停止服务
./xiaozhi-mcp.sh stop

# 重启服务
./xiaozhi-mcp.sh restart

# 查看状态
./xiaozhi-mcp.sh status

# === 日志查看 ===

# 实时查看日志（Ctrl+C 退出）
./xiaozhi-mcp.sh logs

# 查看最近 N 行应用日志
./xiaozhi-mcp.sh log 100          # 查看最近 100 行
./xiaozhi-mcp.sh log              # 默认查看最近 50 行

# 查看错误日志
./xiaozhi-mcp.sh error-logs       # 查看错误日志
./xiaozhi-mcp.sh error-logs 20   # 查看最近 20 行错误

# 搜索日志
./xiaozhi-mcp.sh search-logs "ERROR"        # 搜索 ERROR 关键词
./xiaozhi-mcp.sh search-logs "connecting"   # 搜索连接相关日志

# 查看日志统计信息
./xiaozhi-mcp.sh log-stats         # 查看日志文件大小、行数

# 清空日志
./xiaozhi-mcp.sh clear-logs        # 清空所有日志（需确认）
```

### 特点

- ✅ 简单易用，无需 root 权限
- ✅ 自动管理 PID 文件
- ✅ 支持 nohup 后台运行
- ✅ 日志自动输出到 `app.log` 和 `app.error.log`
- ✅ 彩色输出，状态清晰

---

## 方式二：Systemd Service（推荐用于生产环境）

### 安装步骤

1. 复制 service 文件到系统目录：

```bash
sudo cp xiaozhi-mcp.service /etc/systemd/system/
```

2. 修改路径（如果需要）：

```bash
sudo nano /etc/systemd/system/xiaozhi-mcp.service
# 根据你的实际路径修改 User, WorkingDirectory, ExecStart 等字段
```

3. 重新加载 systemd 配置：

```bash
sudo systemctl daemon-reload
```

4. 启用开机自启（可选）：

```bash
sudo systemctl enable xiaozhi-mcp
```

### 使用方法

```bash
# 启动服务
sudo systemctl start xiaozhi-mcp

# 停止服务
sudo systemctl stop xiaozhi-mcp

# 重启服务
sudo systemctl restart xiaozhi-mcp

# 查看状态
sudo systemctl status xiaozhi-mcp

# 查看实时日志
sudo journalctl -u xiaozhi-mcp -f

# 查看最近日志
sudo journalctl -u xiaozhi-mcp -n 50
```

### 特点

- ✅ 开机自动启动
- ✅ 进程崩溃自动重启（10秒后）
- ✅ 使用 journalctl 统一管理日志
- ✅ 安全性增强（NoNewPrivileges, PrivateTmp）
- ✅ 标准的 Linux 服务管理方式

---

## 日志功能详解

### 实时日志监控
```bash
./xiaozhi-mcp.sh logs
```
- 服务运行时：实时跟踪日志（按 Ctrl+C 退出）
- 服务未运行时：显示最近 50 行日志

### 快速查看日志
```bash
# 查看应用日志（默认 50 行）
./xiaozhi-mcp.sh log

# 查看最近 100 行
./xiaozhi-mcp.sh log 100
```

### 错误日志
```bash
# 查看错误日志
./xiaozhi-mcp.sh error-logs

# 查看最近 20 行错误
./xiaozhi-mcp.sh error-logs 20
```

### 日志搜索
```bash
# 搜索关键词（不区分大小写）
./xiaozhi-mcp.sh search-logs "timeout"
./xiaozhi-mcp.sh search-logs "connection"
./xiaozhi-mcp.sh search-logs "ERROR"
```
- 自动搜索应用日志和错误日志
- 高亮显示匹配的关键词

### 日志统计
```bash
./xiaozhi-mcp.sh log-stats
```
显示：
- 应用日志文件路径、大小、行数
- 错误日志文件路径、大小、行数

### 清空日志
```bash
./xiaozhi-mcp.sh clear-logs
```
- 如果服务正在运行，会先停止
- 清空 `app.log` 和 `app.error.log`
- 需要输入 `yes` 确认

---

## 文件说明

- `xiaozhi-mcp.sh` - Shell 启动脚本
- `xiaozhi-mcp.service` - Systemd 服务配置文件
- `.xiaozhi-mcp.pid` - PID 文件（Shell 脚本使用，自动生成）
- `app.log` - 标准输出日志
- `app.error.log` - 错误日志

---

## 注意事项

1. **Shell 脚本**：
   - ✅ 自动检测脚本所在目录作为项目路径，无需手动修改
   - 直接把脚本放在项目根目录即可使用

2. **Systemd 配置**：
   - ⚠️ 需要手动修改 `xiaozhi-mcp.service` 中的占位符：
     - `YOUR_USERNAME` → 替换为你的用户名
     - `/path/to/xiaozhi-mcp` → 替换为实际项目路径

2. **检查 uv 路径**：
   ```bash
   which uv
   # 确保 uv 在你的 PATH 中，或使用完整路径
   ```

3. **检查配置文件**：
   ```bash
   # 确保 mcp_config.yaml 配置正确
   cat mcp_config.yaml
   ```

4. **防火墙设置**（如果需要远程访问）：
   ```bash
   sudo ufw allow 8080/tcp  # 根据你的端口号调整
   ```

---

## 推荐配置

### 开发环境
使用 **Shell 脚本**，方便调试和查看日志：
```bash
./xiaozhi-mcp.sh start
./xiaozhi-mcp.sh logs  # 随时查看日志
```

### 生产环境
使用 **Systemd**，更稳定可靠：
```bash
sudo systemctl enable xiaozhi-mcp  # 开机自启
sudo systemctl start xiaozhi-mcp   # 立即启动
```

### 配置开机自启动（Shell 脚本方式）

如果想用 Shell 脚本但实现开机自启，可以添加到 crontab：

```bash
crontab -e

# 添加这行：
@reboot cd /home/luca/_projects/ai/xiaozhi/xiaozhi-mcp && ./xiaozhi-mcp.sh start
```

---

## 故障排查

### 服务启动失败

```bash
# 查看错误日志
tail -f app.error.log

# 或使用 systemd
sudo journalctl -u xiaozhi-mcp -n 50 --no-pager
```

### 端口被占用

```bash
# 查看端口占用
sudo lsof -i :8080

# 或
sudo netstat -tulpn | grep 8080
```

### 权限问题

```bash
# 确保脚本有执行权限
chmod +x xiaozhi-mcp.sh

# 确保 uv 可执行
chmod +x ~/.local/bin/uv
```
