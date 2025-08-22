#!/bin/bash

# AcgFun自动签到脚本 - CentOS 7.9 一键安装脚本
# 使用方法: chmod +x install.sh && ./install.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "检测到root用户，建议使用普通用户运行此脚本"
        read -p "是否继续？ (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统版本
check_system() {
    print_info "检查系统版本..."
    
    if [[ ! -f /etc/redhat-release ]]; then
        print_error "此脚本仅支持CentOS/RHEL系统"
        exit 1
    fi
    
    local version=$(cat /etc/redhat-release)
    print_info "系统版本: $version"
    
    if [[ $version == *"CentOS Linux release 7"* ]] || [[ $version == *"Red Hat Enterprise Linux"* ]]; then
        print_success "系统版本检查通过"
    else
        print_warning "系统版本可能不完全兼容，建议使用CentOS 7.9"
    fi
}

# 安装Python 3
install_python() {
    print_info "检查Python 3安装状态..."
    
    # 检查python3是否已安装且版本合适
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version 2>&1 | awk '{print $2}')
        local major_version=$(echo $python_version | cut -d. -f1)
        local minor_version=$(echo $python_version | cut -d. -f2)
        
        if [[ $major_version -eq 3 ]] && [[ $minor_version -ge 6 ]]; then
            print_success "Python $python_version 已安装"
            return 0
        fi
    fi
    
    print_info "安装Python 3..."
    
    # 安装EPEL仓库和Python 3.6
    if ! rpm -q epel-release &> /dev/null; then
        print_info "安装EPEL仓库..."
        sudo yum install -y epel-release
    fi
    
    print_info "安装Python 3.6和pip..."
    sudo yum install -y python36 python36-pip
    
    # 创建软链接（如果不存在）
    if [[ ! -f /usr/bin/python3 ]]; then
        sudo ln -s /usr/bin/python3.6 /usr/bin/python3
    fi
    
    if [[ ! -f /usr/bin/pip3 ]]; then
        sudo ln -s /usr/bin/pip3.6 /usr/bin/pip3
    fi
    
    print_success "Python 3安装完成"
}

# 安装系统依赖
install_dependencies() {
    print_info "安装系统依赖..."
    
    sudo yum install -y git curl wget vim
    
    print_success "系统依赖安装完成"
}

# 创建项目目录
setup_project() {
    print_info "设置项目目录..."
    
    local project_dir="$HOME/acgfun_signin"
    
    if [[ -d "$project_dir" ]]; then
        print_warning "项目目录已存在: $project_dir"
        read -p "是否删除并重新创建？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$project_dir"
        else
            print_info "使用现有目录"
        fi
    fi
    
    mkdir -p "$project_dir"
    cd "$project_dir"
    
    print_success "项目目录设置完成: $project_dir"
    
    # 保存项目目录到环境变量
    export PROJECT_DIR="$project_dir"
}

# 安装Python依赖
install_python_packages() {
    print_info "安装Python依赖包..."
    
    # 升级pip
    python3 -m pip install --user --upgrade pip
    
    # 创建requirements.txt（如果不存在）
    if [[ ! -f requirements.txt ]]; then
        cat > requirements.txt << 'EOF'
requests>=2.31.0
beautifulsoup4>=4.12.2
lxml>=4.9.3
python-dotenv>=1.0.0
schedule>=1.2.0
EOF
    fi
    
    # 安装依赖
    python3 -m pip install --user -r requirements.txt
    
    print_success "Python依赖包安装完成"
}

# 创建配置文件模板
create_config_files() {
    print_info "创建配置文件..."
    
    # 创建sendkey.txt.example
    if [[ ! -f sendkey.txt.example ]]; then
        cat > sendkey.txt.example << 'EOF'
# Server酱SendKey示例文件
# 请将下面的示例SendKey替换为您的真实SendKey
# 
# 获取方法：
# 1. 访问 Server酱官网: https://sct.ftqq.com/
# 2. 微信扫码登录并关注公众号
# 3. 复制您的SendKey
# 4. 将SendKey粘贴到下面（删除这些注释行）
#
# 示例格式：
# SCTxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
    fi
    
    # 创建cookies.txt.example
    if [[ ! -f cookies.txt.example ]]; then
        cat > cookies.txt.example << 'EOF'
# Cookie示例文件
# 请将您从浏览器复制的Cookie内容替换下面的示例内容
# 
# 获取方法：
# 1. 使用浏览器登录 AcgFun.art
# 2. 按F12打开开发者工具
# 3. 在控制台输入: copy(document.cookie)
# 4. 将复制的内容粘贴到 cookies.txt 文件中
#
# 注意：
# - Cookie内容应该是一行，不要换行
# - Cookie中包含多个键值对，用分号和空格分隔
# - 不要包含这些注释行
#
# 示例格式：
key1=value1; key2=value2; key3=value3; session_id=abc123def456; user_token=xyz789; last_visit=1000000000
EOF
    fi
    
    print_success "配置文件模板创建完成"
}

# 创建启动脚本
create_startup_script() {
    print_info "创建启动脚本..."
    
    cat > run_signin.sh << 'EOF'
#!/bin/bash

# AcgFun自动签到启动脚本
PROJECT_DIR="$HOME/acgfun_signin"
cd "$PROJECT_DIR"

echo "==============================================="
echo "开始执行AcgFun自动签到 - $(date)"
echo "==============================================="

# 检查配置文件
if [[ ! -f cookies.txt ]]; then
    echo "错误: cookies.txt文件不存在，请先配置Cookie"
    exit 1
fi

if [[ ! -f sendkey.txt ]]; then
    echo "警告: sendkey.txt文件不存在，将无法发送微信通知"
fi

# 执行签到
python3 cookie_signin.py --file cookies.txt

echo "===============================================" 
echo "签到任务完成 - $(date)"
echo "==============================================="
EOF
    
    chmod +x run_signin.sh
    
    print_success "启动脚本创建完成"
}

# 设置定时任务
setup_crontab() {
    print_info "设置定时任务..."
    
    read -p "是否设置每日自动签到定时任务？ (Y/n): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "跳过定时任务设置"
        return 0
    fi
    
    print_info "请选择签到时间："
    echo "1) 每天上午9点"
    echo "2) 每天上午9点、中午12点、下午6点"
    echo "3) 自定义时间"
    read -p "请选择 (1-3): " -n 1 -r
    echo
    
    local cron_entries=""
    case $REPLY in
        1)
            cron_entries="0 9 * * * cd $PROJECT_DIR && python3 cookie_signin.py --file cookies.txt >> $PROJECT_DIR/cron.log 2>&1"
            ;;
        2)
            cron_entries="0 9 * * * cd $PROJECT_DIR && python3 cookie_signin.py --file cookies.txt >> $PROJECT_DIR/cron.log 2>&1
0 12 * * * cd $PROJECT_DIR && python3 cookie_signin.py --file cookies.txt >> $PROJECT_DIR/cron.log 2>&1
0 18 * * * cd $PROJECT_DIR && python3 cookie_signin.py --file cookies.txt >> $PROJECT_DIR/cron.log 2>&1"
            ;;
        3)
            read -p "请输入cron表达式 (例如: 0 9 * * *): " cron_time
            cron_entries="$cron_time cd $PROJECT_DIR && python3 cookie_signin.py --file cookies.txt >> $PROJECT_DIR/cron.log 2>&1"
            ;;
        *)
            print_warning "无效选择，跳过定时任务设置"
            return 0
            ;;
    esac
    
    # 添加日志清理任务
    read -p "是否设置日志自动清理？ (Y/n): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # 每周日凌晨2点清理日志
        cron_entries="$cron_entries
0 2 * * 0 cd $PROJECT_DIR && python3 log_cleaner.py >> $PROJECT_DIR/cleanup.log 2>&1"
        print_info "已添加每周日凌晨2点的日志清理任务"
    fi
    
    # 备份当前crontab
    crontab -l > /tmp/crontab.backup 2>/dev/null || true
    
    # 添加新的cron任务
    (crontab -l 2>/dev/null || true; echo "$cron_entries") | crontab -
    
    print_success "定时任务设置完成"
    print_info "可以使用 'crontab -l' 查看当前定时任务"
}

# 显示配置指南
show_config_guide() {
    print_info "=========================================="
    print_info "安装完成！请按照以下步骤完成配置："
    print_info "=========================================="
    echo
    print_info "1. 配置Server酱SendKey："
    echo "   cd $PROJECT_DIR"
    echo "   cp sendkey.txt.example sendkey.txt"
    echo "   vim sendkey.txt  # 填入您的SendKey"
    echo
    print_info "2. 配置Cookie："
    echo "   cp cookies.txt.example cookies.txt  # 复制示例文件"
    echo "   vim cookies.txt  # 填入从浏览器复制的Cookie"
    echo
    print_info "3. 测试运行："
    echo "   python3 cookie_signin.py --file cookies.txt"
    echo
    print_info "4. 使用启动脚本："
    echo "   ./run_signin.sh"
    echo
    print_info "5. 手动清理日志："
    echo "   python3 log_cleaner.py"
    echo
    print_info "配置文件位置："
    echo "   项目目录: $PROJECT_DIR"
    echo "   SendKey配置: $PROJECT_DIR/sendkey.txt"
    echo "   Cookie配置: $PROJECT_DIR/cookies.txt"
    echo
    print_info "日志文件："
    echo "   脚本日志: $PROJECT_DIR/cookie_signin.log"
    echo "   定时任务日志: $PROJECT_DIR/cron.log"
    echo "   清理日志: $PROJECT_DIR/cleanup.log"
    echo
    print_success "部署完成！"
}

# 主函数
main() {
    print_info "开始AcgFun自动签到脚本安装..."
    print_info "=========================================="
    
    check_root
    check_system
    install_python
    install_dependencies
    setup_project
    install_python_packages
    create_config_files
    create_startup_script
    setup_crontab
    show_config_guide
}

# 运行主函数
main "$@"