# AcgFun 自动签到脚本

一个基于Cookie认证的 AcgFun.art 网站自动签到脚本，简单稳定，成功率高。

**支持的签到页面**：`https://acgfun.art/

## 功能特点

- 🍪 基于Cookie认证，无需用户名密码
- ✅ 自动执行每日签到
- 🔒 避免账户锁定问题
- 📱 Server酱微信通知（签到成功/失败/Cookie失效）
- 💰 天空石数量获取（签到成功后显示当前积分）
- 🧹 自动日志清理（保持系统整洁）
- 📝 详细的日志记录
- 🌐 智能网络重试机制
- 🔧 SSL错误自动处理
- 🎯 多种签到方式自动识别
- ✔️ 签到状态智能验证

## 安装要求

- Python 3.7 或更高版本
- 网络连接

## 安装步骤

### 1. 克隆或下载项目文件

将所有项目文件下载到本地目录。

### 2. 安装依赖包

在项目目录中打开命令行，运行：

```bash
pip install -r requirements.txt
```

### 3. 获取Cookie

1. 使用浏览器登录 AcgFun.art
2. 按F12打开开发者工具
3. 在控制台中输入以下代码复制Cookie：
   ```javascript
   copy(document.cookie)
   ```
4. 复制 `cookies.txt.example` 为 `cookies.txt` 文件：
   ```bash
   copy cookies.txt.example cookies.txt
   ```
5. 编辑 `cookies.txt` 文件，将复制的Cookie内容粘贴进去

### 4. 配置微信通知（可选）

1. 访问 [Server酱官网](https://sct.ftqq.com/)
2. 微信扫码登录并关注公众号
3. 复制 `sendkey.txt.example` 为 `sendkey.txt`：
   ```bash
   copy sendkey.txt.example sendkey.txt
   ```
4. 编辑 `sendkey.txt` 文件，填入您的SendKey：
   ```
   SCTxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

## 使用方法

### 执行签到

```bash
# 使用cookies.txt文件
python cookie_signin.py --file cookies.txt

# 直接使用Cookie字符串
python cookie_signin.py --cookie "你的Cookie内容"
```

### 单独获取天空石信息

```bash
# 获取当前天空石数量
python credit_analyzer.py --cookies cookies.txt
```

### 验证签到状态

```bash
python verify_signin.py
```

### 日志清理

```bash
# 自动清理过期日志
python log_cleaner.py

# 预览模式（不实际删除）
python log_cleaner.py --dry-run
```

**Cookie方案优势：**
- ✅ 无需密码，避免账户锁定
- ✅ 简单稳定，成功率高
- ✅ 绕过复杂的登录验证
- ✅ 安全性更好

## 日志文件

脚本运行时会生成 `cookie_signin.log` 日志文件，记录详细的执行过程：

- Cookie加载状态
- 登录验证结果
- 签到执行过程
- 错误信息和调试信息
- 执行时间戳

## 安全注意事项

1. **保护您的Cookie**：
   - 请勿将 `cookies.txt` 文件分享给他人
   - 请勿将包含真实Cookie的文件上传到公共代码仓库
   - Cookie具有时效性，过期后需要重新获取

2. **定期更新Cookie**：
   - Cookie会在一段时间后过期
   - 如果签到失败，请重新获取Cookie

## 故障排除

### Cookie验证失败

1. **检查Cookie有效性**：
   - 确保Cookie是最新获取的
   - 尝试手动登录网站验证账户状态

2. **重新获取Cookie**：
   - 清除浏览器缓存
   - 重新登录网站
   - 获取新的Cookie

3. **网络连接问题**：
   - 检查网络连接是否正常
   - 确认可以正常访问 AcgFun.art 网站

4. **网站结构变化**：
   - 如果网站更新了页面结构，脚本可能需要调整
   - 查看日志文件了解具体错误信息

### 签到失败

1. **已经签到**：
   - 脚本会检测是否已经签到过，如果已签到会显示相应信息

2. **Cookie过期**：
   - 重新获取Cookie并更新 `cookies.txt` 文件

3. **网站维护**：
   - 如果网站正在维护，请稍后再试

## 定时签到

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"每天"
4. 设置操作为启动程序：`python`
5. 添加参数：`cookie_signin.py --file cookies.txt`
6. 设置起始位置为脚本所在目录

### Linux Cron

```bash
# 编辑crontab
crontab -e

# 添加每天上午9点执行签到
0 9 * * * cd /path/to/project && python cookie_signin.py --file cookies.txt
```

## CentOS 7.9 部署指南

### 快速部署（推荐）

1. **下载项目文件到CentOS服务器**
2. **运行一键安装脚本**：
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
3. **按照提示配置Cookie和SendKey**

### 手动部署

详细部署说明请参考：[DEPLOY.md](DEPLOY.md)

### 配置要点

1. **获取SendKey**：访问 [Server酱官网](https://sct.ftqq.com/)
2. **获取Cookie**：浏览器控制台运行 `copy(document.cookie)`
3. **设置定时任务**：使用crontab设置每日自动签到

## 项目文件说明

**核心功能文件：**
- `cookie_signin.py` - 主要的Cookie签到脚本（包含微信通知和天空石信息）
- `verify_signin.py` - 签到状态验证脚本
- `wechat_notifier.py` - Server酱微信通知模块
- `credit_analyzer.py` - 天空石积分分析脚本
- `log_cleaner.py` - 日志自动清理脚本

**配置文件：**
- `cookies.txt` - Cookie数据文件
- `cookies.txt.example` - Cookie配置示例文件
- `sendkey.txt` - Server酱SendKey配置文件
- `sendkey.txt.example` - SendKey配置示例

**部署文件：**
- `DEPLOY.md` - CentOS 7.9详细部署说明
- `install.sh` - 一键安装脚本
- `requirements.txt` - Python依赖包列表

**项目文档：**
- `README.md` - 项目说明文档
- `.gitignore` - Git忽略文件配置

添加到 crontab：
```bash
# 每天上午9点执行签到
0 9 * * * /usr/bin/python3 /path/to/acgfun_sign.py --once
```

## 免责声明

此脚本仅供学习和个人使用。使用此脚本时请遵守 AcgFun.art 网站的服务条款。作者不对使用此脚本可能产生的任何后果负责。

## 支持

如果遇到问题，请：

1. 检查日志文件 `acgfun_sign.log`
2. 确认网络连接和凭据
3. 查看是否有网站结构更新

## 更新日志

### v1.0.0
- 初始版本发布
- 支持自动登录和签到
- 支持定时任务
- 完整的日志记录功能