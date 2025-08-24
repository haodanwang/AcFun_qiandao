# AcgFun自动签到脚本 - CentOS 7.9 部署说明

本文档详细说明如何在CentOS 7.9系统上部署和配置AcgFun自动签到脚本。

## 系统要求

- 操作系统：CentOS 7.9 (x86_64)
- Python：3.6+ （建议3.7+）
- 网络：能够访问互联网
- 权限：普通用户权限即可

## 一、环境准备

### 1. 更新系统
```bash
sudo yum update -y
```

### 2. 安装Python 3.7+
CentOS 7.9默认Python版本较低，需要安装较新版本：

```bash
# 安装开发工具
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel

# 方法1：使用EPEL仓库安装Python 3.6
sudo yum install -y epel-release
sudo yum install -y python36 python36-pip

# 方法2：编译安装Python 3.8（推荐）
cd /tmp
wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tgz
tar -xzf Python-3.8.10.tgz
cd Python-3.8.10
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall

# 创建软链接
sudo ln -s /usr/local/bin/python3.8 /usr/local/bin/python3
sudo ln -s /usr/local/bin/pip3.8 /usr/local/bin/pip3
```

### 3. 验证Python安装
```bash
python3 --version
pip3 --version
```

### 4. 安装必要的系统依赖
```bash
sudo yum install -y git curl wget vim
```

## 二、项目部署

### 1. 创建项目目录
```bash
# 创建项目目录
mkdir -p ~/acgfun_signin
cd ~/acgfun_signin
```

### 2. 下载项目文件
根据您的项目获取方式，选择以下方法之一：

**方法1：从Git仓库克隆**
```bash
git clone <your-repo-url> .
```

**方法2：手动上传文件**
将以下核心文件上传到服务器的 `~/acgfun_signin` 目录：
- `cookie_signin.py`
- `credit_analyzer.py`
- `verify_signin.py` 
- `wechat_notifier.py`
- `log_cleaner.py`
- `requirements.txt`
- `config/sendkey.txt.example`
- `config/cookies.txt.example`
- `install.sh`
- `README.md`
- `DEPLOY.md`
- `.gitignore`

**方法3：使用scp上传**
```bash
# 在本地执行（替换为实际的服务器IP和路径）
scp -r /path/to/local/project/* user@server_ip:~/acgfun_signin/
```

### 3. 安装Python依赖
```bash
cd ~/acgfun_signin

# 升级pip
pip3 install --upgrade pip

# 安装项目依赖
pip3 install -r requirements.txt

# 如果pip3安装失败，尝试使用用户目录安装
pip3 install --user -r requirements.txt
```

## 三、配置文件设置

### 1. 创建配置目录
```bash
# 创建配置和日志目录
mkdir -p config logs
```

### 2. 配置Server酱SendKey
```bash
# 复制示例文件
cp config/sendkey.txt.example config/sendkey.txt

# 编辑配置文件
vim config/sendkey.txt
```

在`config/sendkey.txt`中填入您的Server酱SendKey：
```
SCTxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

获取SendKey的方法：
1. 访问 [Server酱官网](https://sct.ftqq.com/)
2. 微信扫码登录并关注公众号
3. 复制您的SendKey

### 3. 配置Cookie
```bash
# 创建Cookie文件
touch config/cookies.txt
vim config/cookies.txt
```

在`config/cookies.txt`中填入从浏览器复制的Cookie：
```
key1=value1; key2=value2; key3=value3; session_id=abc123def456; user_token=xyz789
```

获取Cookie的方法：
1. 使用浏览器登录 AcgFun.art
2. 按F12打开开发者工具
3. 在控制台输入：`copy(document.cookie)`
4. 将复制的内容粘贴到`config/cookies.txt`文件中

### 4. 设置文件权限
```bash
# 设置适当的文件权限
chmod 600 config/cookies.txt config/sendkey.txt
chmod 755 *.py
```

## 四、功能测试

### 1. 测试Python脚本
```bash
# 测试脚本是否能正常运行
python3 cookie_signin.py --help
```

### 2. 测试Cookie有效性
```bash
# 验证签到状态
python3 verify_signin.py
```

### 3. 测试微信通知
直接运行签到脚本测试：
```bash
# 测试签到功能和微信通知
python3 cookie_signin.py

# 测试带日志清理功能
python3 cookie_signin.py --clean-logs

# 单独测试天空石信息获取
python3 credit_analyzer.py
```

## 五、自动化配置

### 1. 创建定时任务
使用crontab设置每日自动签到：

```bash
# 编辑crontab
crontab -e

# 添加以下内容（每天上午9点执行，带日志清理）
0 9 * * * cd ~/acgfun_signin && python3 cookie_signin.py --clean-logs >> ~/acgfun_signin/logs/cron.log 2>&1

# 可选：添加多个时间点提高成功率
0 9 * * * cd ~/acgfun_signin && python3 cookie_signin.py --clean-logs >> ~/acgfun_signin/logs/cron.log 2>&1
0 12 * * * cd ~/acgfun_signin && python3 cookie_signin.py >> ~/acgfun_signin/logs/cron.log 2>&1
0 18 * * * cd ~/acgfun_signin && python3 cookie_signin.py >> ~/acgfun_signin/logs/cron.log 2>&1
```

### 2. 查看crontab任务
```bash
# 查看当前的定时任务
crontab -l
```

### 3. 创建启动脚本（可选）
创建一个便于执行的启动脚本：

```bash
cat > ~/acgfun_signin/run_signin.sh << 'EOF'
#!/bin/bash

# AcgFun自动签到启动脚本
cd ~/acgfun_signin

echo "==============================================="
echo "开始执行AcgFun自动签到 - $(date)"
echo "==============================================="

# 执行签到（带日志清理）
python3 cookie_signin.py --clean-logs

echo "===============================================" 
echo "签到任务完成 - $(date)"
echo "==============================================="
EOF

# 设置执行权限
chmod +x ~/acgfun_signin/run_signin.sh
```

## 六、日志管理

### 1. 日志文件位置
- 签到日志：`~/acgfun_signin/logs/cookie_signin.log`
- Cron日志：`~/acgfun_signin/logs/cron.log`
- 清理日志：`~/acgfun_signin/logs/cleanup.log`

### 2. 自动日志清理
项目包含自动日志清理功能：

```bash
# 手动运行日志清理
python3 log_cleaner.py

# 预览将要清理的文件（不实际删除）
python3 log_cleaner.py --dry-run

# 指定目录进行清理
python3 log_cleaner.py --dir /path/to/project
```

**清理规则：**
- `cookie_signin.log` - 保疙7天
- `cron.log` - 保疙30天
- 其他`.log`文件 - 保疙7天
- 自动删除空日志文件

### 3. 定时清理设置
使用--clean-logs参数集成到签到命令中（推荐）：
```bash
# 签到时自动清理（已包含在上面的crontab配置中）
python3 cookie_signin.py --clean-logs
```

或者手动添加单独的清理任务（每周日凌晨2点）：
```bash
echo "0 2 * * 0 cd ~/acgfun_signin && python3 log_cleaner.py >> ~/acgfun_signin/logs/cleanup.log 2>&1" | crontab -
```

### 4. 日志轮转（可选）
创建logrotate配置防止日志文件过大：

```bash
sudo vim /etc/logrotate.d/acgfun_signin
```

添加以下内容：
```
/home/*/acgfun_signin/*.log {
    daily
    missingok
    rotate 30
    compress
    notifempty
    create 644
}
```

## 七、故障排除

### 1. 常见问题

**Python版本问题**
```bash
# 检查Python版本
python3 --version

# 如果版本过低，重新安装较新版本的Python
```

**依赖安装失败**
```bash
# 尝试使用用户目录安装
pip3 install --user -r requirements.txt

# 或者升级pip
pip3 install --upgrade pip
```

**SSL证书问题**
```bash
# 更新ca证书
sudo yum update -y ca-certificates
```

**网络连接问题**
```bash
# 测试网络连接
curl -I https://acgfun.art
ping acgfun.art
```

### 2. 查看日志
```bash
# 查看最新的签到日志
tail -f ~/acgfun_signin/logs/cookie_signin.log

# 查看cron日志
tail -f ~/acgfun_signin/logs/cron.log

# 查看系统cron日志
sudo tail -f /var/log/cron
```

### 3. 调试模式
```bash
# 手动运行脚本查看详细输出
cd ~/acgfun_signin
python3 cookie_signin.py

# 测试天空石信息获取
python3 credit_analyzer.py

# 测试日志清理功能
python3 log_cleaner.py --dry-run
```

## 八、安全建议

### 1. 文件权限
```bash
# 确保敏感文件权限正确
chmod 600 config/cookies.txt config/sendkey.txt
chmod 755 ~/acgfun_signin
```

### 2. 防火墙（如果启用）
```bash
# 检查防火墙状态
sudo systemctl status firewalld

# 如果需要，允许HTTPS出站连接（通常默认允许）
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 定期更新
```bash
# 定期更新系统和Python包
sudo yum update -y
pip3 install --upgrade -r requirements.txt
```

## 九、监控和维护

### 1. 监控签到状态
通过微信通知可以实时了解签到状态。如果长期没有收到通知，检查：
- Cookie是否过期
- SendKey是否有效
- 网络连接是否正常

### 2. Cookie维护
Cookie会定期过期，需要重新获取：
```bash
# 更新Cookie
vim ~/acgfun_signin/config/cookies.txt
```

### 3. 备份配置
```bash
# 备份重要配置文件
cp config/cookies.txt config/cookies.txt.backup
cp config/sendkey.txt config/sendkey.txt.backup
```

## 十、卸载说明

### 使用卸载脚本（推荐）

项目提供了安全的卸载脚本，可以自动备份配置文件并清理安装：

```bash
# 运行卸载脚本
cd ~/acgfun_signin
chmod +x uninstall.sh
./uninstall.sh
```

**卸载脚本功能**：
- 自动检测和备份配置文件（cookies.txt、sendkey.txt）
- 多种备份选项：主目录、桌面、自定义目录
- 清除所有相关的crontab定时任务
- 删除安装目录和相关文件
- 清理日志文件和Python缓存
- 生成备份说明文档

### 手动卸载

如需手动卸载，执行以下步骤：

```bash
# 1. 备份配置文件
cp config/cookies.txt ~/cookies_backup.txt
cp config/sendkey.txt ~/sendkey_backup.txt

# 2. 删除crontab任务
crontab -e
# 手动删除相关行

# 3. 删除项目目录
rm -rf ~/acgfun_signin

# 4. 删除logrotate配置（如果创建了）
sudo rm -f /etc/logrotate.d/acgfun_signin
```

---

## 快速部署命令汇总

```bash
# 1. 创建目录并进入
mkdir -p ~/acgfun_signin && cd ~/acgfun_signin

# 2. 上传项目文件（手动）

# 3. 创建配置和日志目录
mkdir -p config logs

# 4. 安装依赖
pip3 install -r requirements.txt

# 5. 配置文件
cp config/sendkey.txt.example config/sendkey.txt
vim config/sendkey.txt  # 填入SendKey
vim config/cookies.txt  # 填入Cookie

# 6. 设置权限
chmod 600 config/cookies.txt config/sendkey.txt
chmod 755 *.py

# 7. 测试运行
python3 cookie_signin.py

# 8. 设置定时任务（包含签到和日志清理）
echo "0 9 * * * cd ~/acgfun_signin && python3 cookie_signin.py --clean-logs >> ~/acgfun_signin/logs/cron.log 2>&1" | crontab -
```

部署完成后，您将拥有一个完全自动化的AcgFun签到系统，包含微信通知、天空石信息获取和自动日志清理功能！