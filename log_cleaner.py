#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志清理脚本
自动清理过期的日志文件，保持系统整洁
"""

import os
import time
import glob
import logging
from datetime import datetime, timedelta

class LogCleaner:
    def __init__(self, project_dir: str = None):
        """
        初始化日志清理器
        
        Args:
            project_dir: 项目目录路径，默认为当前目录
        """
        self.project_dir = project_dir or os.path.dirname(os.path.abspath(__file__))
        self.logs_dir = os.path.join(self.project_dir, 'logs')
        
        # 确保日志目录存在
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # 配置清理规则（现在在logs目录中查找）
        self.cleanup_rules = {
            'cookie_signin.log': 7,      # 保留7天的签到日志
            'cron.log': 30,              # 保留30天的定时任务日志
            'cleanup.log': 30,           # 保留30天的清理日志
            '*.log': 7,                  # 其他日志文件保留7天
        }
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def get_file_age_days(self, file_path: str) -> int:
        """
        获取文件的天数
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件创建天数
        """
        try:
            file_time = os.path.getctime(file_path)
            file_date = datetime.fromtimestamp(file_time)
            current_date = datetime.now()
            return (current_date - file_date).days
        except Exception as e:
            logging.error(f"获取文件时间失败 {file_path}: {e}")
            return 0

    def clean_log_files(self) -> dict:
        """
        清理日志文件
        
        Returns:
            dict: 清理结果统计
        """
        result = {
            'cleaned_files': [],
            'total_size': 0,
            'error_files': []
        }
        
        logging.info("开始清理日志文件...")
        
        for pattern, max_days in self.cleanup_rules.items():
            # 在logs目录中查找匹配的文件
            file_pattern = os.path.join(self.logs_dir, pattern)
            matching_files = glob.glob(file_pattern)
            
            for file_path in matching_files:
                try:
                    # 跳过目录
                    if os.path.isdir(file_path):
                        continue
                    
                    # 检查文件年龄
                    file_age = self.get_file_age_days(file_path)
                    
                    if file_age > max_days:
                        # 获取文件大小
                        file_size = os.path.getsize(file_path)
                        
                        # 删除文件
                        os.remove(file_path)
                        
                        result['cleaned_files'].append({
                            'file': os.path.basename(file_path),
                            'age_days': file_age,
                            'size_bytes': file_size
                        })
                        result['total_size'] += file_size
                        
                        logging.info(f"已删除过期日志: {os.path.basename(file_path)} (年龄: {file_age}天, 大小: {file_size}字节)")
                    
                except Exception as e:
                    logging.error(f"删除文件失败 {file_path}: {e}")
                    result['error_files'].append({
                        'file': file_path,
                        'error': str(e)
                    })
        
        return result

    def clean_empty_logs(self):
        """清理空的日志文件"""
        log_files = glob.glob(os.path.join(self.logs_dir, "*.log"))
        
        for log_file in log_files:
            try:
                if os.path.getsize(log_file) == 0:
                    os.remove(log_file)
                    logging.info(f"已删除空日志文件: {os.path.basename(log_file)}")
            except Exception as e:
                logging.error(f"删除空日志文件失败 {log_file}: {e}")

    def get_disk_usage(self) -> dict:
        """获取logs目录磁盘使用情况"""
        try:
            total_size = 0
            file_count = 0
            
            for file_path in glob.glob(os.path.join(self.logs_dir, "*")):
                if os.path.isfile(file_path):
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count
            }
        except Exception as e:
            logging.error(f"获取磁盘使用情况失败: {e}")
            return {}

    def run_cleanup(self) -> bool:
        """
        运行完整的清理流程
        
        Returns:
            bool: 清理是否成功
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"开始日志清理任务 - {current_time}")
            
            # 获取清理前的磁盘使用情况
            before_usage = self.get_disk_usage()
            
            # 清理过期日志
            cleanup_result = self.clean_log_files()
            
            # 清理空日志文件
            self.clean_empty_logs()
            
            # 获取清理后的磁盘使用情况
            after_usage = self.get_disk_usage()
            
            # 输出清理结果
            cleaned_count = len(cleanup_result['cleaned_files'])
            total_saved_mb = round(cleanup_result['total_size'] / (1024 * 1024), 2)
            
            logging.info(f"清理完成:")
            logging.info(f"  删除文件数: {cleaned_count}")
            logging.info(f"  释放空间: {total_saved_mb} MB")
            logging.info(f"  错误文件数: {len(cleanup_result['error_files'])}")
            
            if before_usage and after_usage:
                logging.info(f"  目录总大小: {before_usage['total_size_mb']} MB -> {after_usage['total_size_mb']} MB")
            
            return len(cleanup_result['error_files']) == 0
            
        except Exception as e:
            logging.error(f"日志清理任务失败: {e}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AcgFun签到脚本日志清理工具')
    parser.add_argument('--dir', type=str, help='项目目录路径')
    parser.add_argument('--dry-run', action='store_true', help='只显示将要删除的文件，不实际删除')
    
    args = parser.parse_args()
    
    # 创建清理器
    cleaner = LogCleaner(args.dir)
    
    if args.dry_run:
        print("预览模式 - 不会实际删除文件")
        # 这里可以添加预览逻辑
        return
    
    # 运行清理
    success = cleaner.run_cleanup()
    
    if success:
        print("✅ 日志清理完成")
    else:
        print("❌ 日志清理过程中出现错误")
        exit(1)

if __name__ == '__main__':
    main()