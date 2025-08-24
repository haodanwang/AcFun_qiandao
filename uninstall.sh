#!/bin/bash

# AcgFun自动签到脚本 - 卸载脚本
# 功能：安全卸载脚本，清理安装目录、定时任务和日志，备份配置文件

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_blue() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 显示横幅
show_banner() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "    AcgFun自动签到脚本 - 卸载工具 v1.0"
    echo "=================================================="
    echo -e "${NC}"
}

# 检查运行环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查是否为Linux系统
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        log_warn "此脚本主要为Linux系统设计"
    fi
    
    # 检查是否有写权限
    if [[ ! -w "$(pwd)" ]]; then
        log_error "当前目录没有写权限，请检查权限设置"
        exit 1
    fi
    
    log_info "环境检查完成"
}

# 确认卸载
confirm_uninstall() {
    echo -e "${YELLOW}"
    echo "=================================================="
    echo "                  ⚠️  警告  ⚠️"
    echo "=================================================="
    echo "此操作将会："
    echo "  1. 备份您的配置文件到指定目录"
    echo "  2. 清除所有crontab定时任务"
    echo "  3. 删除项目安装目录"
    echo "  4. 清理所有相关日志文件"
    echo ""
    echo "⚠️  此操作不可逆，请确保您已经备份重要数据！"
    echo "=================================================="
    echo -e "${NC}"
    
    read -p "您确定要继续卸载吗？(输入 'YES' 继续，其他键取消): " confirm
    
    if [[ "$confirm" != "YES" ]]; then
        log_info "卸载已取消"
        exit 0
    fi
}

# 选择备份目录
choose_backup_dir() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "              配置文件备份选项"
    echo "=================================================="
    echo "1. 当前用户主目录 (~)"
    echo "2. 桌面目录 (~/Desktop 或 ~/桌面)"
    echo "3. 自定义目录"
    echo "4. 不备份配置文件"
    echo "=================================================="
    echo -e "${NC}"
    
    while true; do
        read -p "请选择备份目录 [1-4]: " choice
        
        case $choice in
            1)
                BACKUP_DIR="$HOME/acgfun_backup_$(date +%Y%m%d_%H%M%S)"
                break
                ;;
            2)
                if [[ -d "$HOME/Desktop" ]]; then
                    BACKUP_DIR="$HOME/Desktop/acgfun_backup_$(date +%Y%m%d_%H%M%S)"
                elif [[ -d "$HOME/桌面" ]]; then
                    BACKUP_DIR="$HOME/桌面/acgfun_backup_$(date +%Y%m%d_%H%M%S)"
                else
                    BACKUP_DIR="$HOME/acgfun_backup_$(date +%Y%m%d_%H%M%S)"
                fi
                break
                ;;
            3)
                read -p "请输入自定义备份目录路径: " custom_dir
                if [[ -n "$custom_dir" ]]; then
                    BACKUP_DIR="$custom_dir/acgfun_backup_$(date +%Y%m%d_%H%M%S)"
                    break
                else
                    log_error "路径不能为空，请重新选择"
                fi
                ;;
            4)
                BACKUP_DIR=""
                log_warn "您选择不备份配置文件"
                break
                ;;
            *)
                log_error "无效选择，请输入 1-4"
                ;;
        esac
    done
}

# 备份配置文件
backup_config_files() {
    if [[ -z "$BACKUP_DIR" ]]; then
        log_info "跳过配置文件备份"
        return 0
    fi
    
    log_info "开始备份配置文件..."
    
    # 创建备份目录
    if ! mkdir -p "$BACKUP_DIR"; then
        log_error "无法创建备份目录: $BACKUP_DIR"
        return 1
    fi
    
    # 备份文件列表
    local backup_files=(
        "config/cookies.txt"
        "config/sendkey.txt"
    )
    
    local backup_count=0
    
    for file in "${backup_files[@]}"; do
        if [[ -f "$file" ]]; then
            if cp "$file" "$BACKUP_DIR/$(basename "$file")"; then
                log_info "✅ 已备份: $file"
                backup_count=$((backup_count + 1))
            else
                log_error "❌ 备份失败: $file"
            fi
        else
            log_warn "⚠️  文件不存在: $file"
        fi
    done
    
    # 创建备份说明文件
    cat > "$BACKUP_DIR/README.txt" << EOF
AcgFun自动签到脚本 - 配置文件备份
========================================

备份时间: $(date)
备份目录: $BACKUP_DIR
项目目录: $(pwd)

备份文件说明:
- cookies.txt: Cookie配置文件（包含登录信息）
- sendkey.txt: Server酱SendKey配置文件（用于微信通知）

使用说明:
1. 重新安装脚本后，将这些文件复制到 config/ 目录下
2. 确保文件权限设置为 600 (chmod 600 config/cookies.txt config/sendkey.txt)
3. 测试运行确认配置正确

注意事项:
- 请妥善保管这些配置文件，它们包含敏感信息
- Cookie会定期过期，如果备份时间较长，可能需要重新获取
- SendKey长期有效，可以直接使用

技术支持:
如需重新部署，请参考项目文档 README.md 和 DEPLOY.md
EOF
    
    if [[ $backup_count -gt 0 ]]; then
        log_info "✅ 配置文件备份完成！"
        log_info "📁 备份位置: $BACKUP_DIR"
        log_info "📋 备份了 $backup_count 个配置文件"
    else
        log_warn "⚠️  没有找到可备份的配置文件"
        # 删除空的备份目录
        rmdir "$BACKUP_DIR" 2>/dev/null
    fi
}

# 清除定时任务
remove_cron_jobs() {
    log_info "清除crontab定时任务..."
    
    # 获取当前crontab
    local current_cron
    current_cron=$(crontab -l 2>/dev/null)
    
    if [[ -z "$current_cron" ]]; then
        log_info "没有发现crontab定时任务"
        return 0
    fi
    
    # 过滤掉包含acgfun相关的任务
    local new_cron
    new_cron=$(echo "$current_cron" | grep -v -E "(acgfun|cookie_signin|credit_analyzer|log_cleaner)" || true)
    
    # 计算删除的任务数
    local old_count new_count removed_count
    old_count=$(echo "$current_cron" | wc -l)
    new_count=$(echo "$new_cron" | wc -l)
    removed_count=$((old_count - new_count))
    
    # 更新crontab
    if [[ $removed_count -gt 0 ]]; then
        if [[ -n "$new_cron" ]]; then
            echo "$new_cron" | crontab -
        else
            crontab -r 2>/dev/null || true
        fi
        log_info "✅ 已清除 $removed_count 个相关定时任务"
    else
        log_info "没有发现相关的定时任务"
    fi
}

# 获取安装目录
get_install_directories() {
    INSTALL_DIRS=()
    
    # 当前目录（如果包含签到脚本）
    if [[ -f "cookie_signin.py" ]]; then
        INSTALL_DIRS+=("$(pwd)")
    fi
    
    # 常见安装目录
    local common_dirs=(
        "$HOME/acgfun_signin"
        "/opt/acgfun_signin"
        "/usr/local/acgfun_signin"
    )
    
    for dir in "${common_dirs[@]}"; do
        if [[ -d "$dir" && -f "$dir/cookie_signin.py" ]]; then
            INSTALL_DIRS+=("$dir")
        fi
    done
    
    # 去重
    INSTALL_DIRS=($(printf "%s\n" "${INSTALL_DIRS[@]}" | sort -u))
}

# 选择要删除的目录
choose_directories_to_remove() {
    get_install_directories
    
    if [[ ${#INSTALL_DIRS[@]} -eq 0 ]]; then
        log_warn "没有发现AcgFun签到脚本的安装目录"
        return 0
    fi
    
    echo -e "${BLUE}"
    echo "=================================================="
    echo "            发现以下安装目录"
    echo "=================================================="
    
    local i=1
    for dir in "${INSTALL_DIRS[@]}"; do
        echo "$i. $dir"
        i=$((i + 1))
    done
    
    echo "$i. 全部删除"
    echo "$((i + 1)). 跳过目录删除"
    echo "=================================================="
    echo -e "${NC}"
    
    while true; do
        read -p "请选择要删除的目录 [1-$((i + 1))]: " choice
        
        if [[ "$choice" =~ ^[0-9]+$ ]]; then
            if [[ $choice -ge 1 && $choice -le ${#INSTALL_DIRS[@]} ]]; then
                DIRS_TO_REMOVE=("${INSTALL_DIRS[$((choice - 1))]}")
                break
            elif [[ $choice -eq $i ]]; then
                DIRS_TO_REMOVE=("${INSTALL_DIRS[@]}")
                break
            elif [[ $choice -eq $((i + 1)) ]]; then
                DIRS_TO_REMOVE=()
                break
            fi
        fi
        
        log_error "无效选择，请输入 1-$((i + 1))"
    done
}

# 删除安装目录
remove_install_directories() {
    if [[ ${#DIRS_TO_REMOVE[@]} -eq 0 ]]; then
        log_info "跳过目录删除"
        return 0
    fi
    
    log_info "开始删除安装目录..."
    
    for dir in "${DIRS_TO_REMOVE[@]}"; do
        if [[ -d "$dir" ]]; then
            log_info "正在删除目录: $dir"
            
            # 安全检查，避免删除重要目录
            if [[ "$dir" == "/" || "$dir" == "$HOME" || "$dir" == "/usr" || "$dir" == "/opt" ]]; then
                log_error "安全检查失败：拒绝删除系统重要目录 $dir"
                continue
            fi
            
            if rm -rf "$dir"; then
                log_info "✅ 已删除: $dir"
            else
                log_error "❌ 删除失败: $dir"
            fi
        else
            log_warn "⚠️  目录不存在: $dir"
        fi
    done
}

# 清理用户目录中的日志文件
clean_user_logs() {
    log_info "清理用户目录中的相关日志文件..."
    
    local log_patterns=(
        "$HOME/acgfun*.log"
        "$HOME/cookie_signin*.log"
        "$HOME/cron*.log"
        "$HOME/cleanup*.log"
    )
    
    local cleaned_count=0
    
    for pattern in "${log_patterns[@]}"; do
        for file in $pattern; do
            if [[ -f "$file" ]]; then
                if rm -f "$file"; then
                    log_info "✅ 已清理日志: $file"
                    cleaned_count=$((cleaned_count + 1))
                fi
            fi
        done
    done
    
    if [[ $cleaned_count -eq 0 ]]; then
        log_info "没有发现需要清理的日志文件"
    else
        log_info "✅ 已清理 $cleaned_count 个日志文件"
    fi
}

# 清理Python缓存
clean_python_cache() {
    log_info "清理Python缓存文件..."
    
    # 在当前目录查找并删除__pycache__目录
    if find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null; then
        log_info "✅ 已清理Python缓存文件"
    fi
    
    # 删除.pyc文件
    if find . -name "*.pyc" -delete 2>/dev/null; then
        log_info "✅ 已清理.pyc文件"
    fi
}

# 显示卸载结果
show_uninstall_result() {
    echo -e "${GREEN}"
    echo "=================================================="
    echo "                 卸载完成！"
    echo "=================================================="
    echo -e "${NC}"
    
    if [[ -n "$BACKUP_DIR" && -d "$BACKUP_DIR" ]]; then
        echo -e "${YELLOW}📁 配置文件备份位置:${NC}"
        echo "   $BACKUP_DIR"
        echo ""
    fi
    
    echo -e "${BLUE}✅ 已完成的操作:${NC}"
    echo "   ✓ 清除了相关的crontab定时任务"
    echo "   ✓ 删除了安装目录和相关文件"
    echo "   ✓ 清理了日志文件和Python缓存"
    
    if [[ -n "$BACKUP_DIR" ]]; then
        echo "   ✓ 备份了配置文件到安全位置"
    fi
    
    echo ""
    echo -e "${YELLOW}💡 重新安装说明:${NC}"
    echo "   1. 重新下载或克隆项目代码"
    echo "   2. 运行 ./install.sh 进行安装"
    echo "   3. 将备份的配置文件复制到 config/ 目录"
    echo "   4. 设置正确的文件权限并测试运行"
    echo ""
    echo "感谢您使用AcgFun自动签到脚本！"
}

# 主函数
main() {
    show_banner
    check_environment
    confirm_uninstall
    
    echo ""
    log_info "开始卸载流程..."
    
    # 1. 选择备份目录并备份配置
    choose_backup_dir
    backup_config_files
    
    echo ""
    
    # 2. 清除定时任务
    remove_cron_jobs
    
    echo ""
    
    # 3. 选择并删除安装目录
    choose_directories_to_remove
    remove_install_directories
    
    echo ""
    
    # 4. 清理日志和缓存
    clean_user_logs
    clean_python_cache
    
    echo ""
    
    # 5. 显示结果
    show_uninstall_result
}

# 信号处理
trap 'echo -e "\n${RED}用户中断卸载过程${NC}"; exit 1' INT TERM

# 运行主函数
main "$@"
