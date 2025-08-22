#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Server酱个人微信通知模块
使用Server酱服务发送消息到个人微信
官网: https://sct.ftqq.com/
"""

import requests
import json
import logging
from datetime import datetime
from typing import Optional

class ServerChanNotifier:
    def __init__(self, sendkey: Optional[str] = None):
        """
        初始化Server酱通知器
        
        Args:
            sendkey: Server酱的SendKey
        """
        self.sendkey = sendkey
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL验证
        self.api_url = "https://sctapi.ftqq.com/{sendkey}.send"
        
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def set_sendkey(self, sendkey: str):
        """设置SendKey"""
        self.sendkey = sendkey

    def send_message(self, title: str, desp: str = "") -> bool:
        """
        发送消息到微信
        
        Args:
            title: 消息标题
            desp: 消息内容（支持Markdown格式）
            
        Returns:
            bool: 发送是否成功
        """
        if not self.sendkey:
            logging.warning("⚠️ 未设置Server酱SendKey，跳过微信通知")
            return False
        
        url = self.api_url.format(sendkey=self.sendkey)
        
        data = {
            "title": title,
            "desp": desp
        }
        
        try:
            response = self.session.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    logging.info("✅ Server酱微信通知发送成功")
                    return True
                else:
                    logging.error(f"❌ Server酱通知发送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                logging.error(f"❌ Server酱请求失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"❌ 发送Server酱通知时发生错误: {e}")
            return False

    def notify_signin_success(self, username: str = "", signin_info: str = "") -> bool:
        """
        发送签到成功通知
        
        Args:
            username: 用户名
            signin_info: 签到详细信息
            
        Returns:
            bool: 发送是否成功
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        title = "🎉 AcgFun签到成功"
        
        desp = f"""## 签到详情

**时间**: {current_time}
**用户**: {username if username else '未知用户'}
**状态**: ✅ 签到完成

{signin_info if signin_info else '今日签到任务已完成！'}

---
*AcgFun自动签到系统*"""
        
        return self.send_message(title, desp)

    def notify_signin_failed(self, username: str = "", error_msg: str = "") -> bool:
        """
        发送签到失败通知
        
        Args:
            username: 用户名
            error_msg: 错误信息
            
        Returns:
            bool: 发送是否成功
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        title = "❌ AcgFun签到失败"
        
        desp = f"""## 签到失败详情

**时间**: {current_time}
**用户**: {username if username else '未知用户'}
**状态**: ❌ 签到失败

**错误信息**: {error_msg if error_msg else '未知错误'}

## 建议操作
- 检查网络连接
- 更新Cookie信息
- 查看详细日志

---
*AcgFun自动签到系统*"""
        
        return self.send_message(title, desp)

    def notify_cookie_expired(self, username: str = "") -> bool:
        """
        发送Cookie失效通知
        
        Args:
            username: 用户名
            
        Returns:
            bool: 发送是否成功
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        title = "🚨 Cookie失效警告"
        
        desp = f"""## Cookie失效提醒

**时间**: {current_time}
**用户**: {username if username else '未知用户'}
**状态**: ⚠️ Cookie已失效

## 需要操作
1. 重新登录AcgFun网站
2. 获取新的Cookie
3. 更新cookies.txt文件

## 获取Cookie方法
- 浏览器按F12打开开发者工具
- 在控制台输入: `copy(document.cookie)`
- 将复制的内容保存到cookies.txt

---
*AcgFun自动签到系统*"""
        
        return self.send_message(title, desp)

    def notify_already_signed(self, username: str = "") -> bool:
        """
        发送已签到通知
        
        Args:
            username: 用户名
            
        Returns:
            bool: 发送是否成功
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        title = "ℹ️ AcgFun签到状态"
        
        desp = f"""## 签到状态检查

**时间**: {current_time}
**用户**: {username if username else '未知用户'}
**状态**: ✅ 今日已签到

今天已经完成签到，无需重复操作。

---
*AcgFun自动签到系统*"""
        
        return self.send_message(title, desp)

def load_sendkey_from_file(file_path: str = "sendkey.txt") -> Optional[str]:
    """
    从文件加载Server酱SendKey
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: SendKey或None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sendkey = f.read().strip()
            if sendkey and len(sendkey) > 10:  # SendKey通常比较长
                return sendkey
    except FileNotFoundError:
        logging.info(f"未找到{file_path}文件，跳过微信通知")
    except Exception as e:
        logging.error(f"读取{file_path}文件失败: {e}")
    
    return None

# 向后兼容的别名
WeChatNotifier = ServerChanNotifier
load_webhook_url_from_file = load_sendkey_from_file

# 示例用法
if __name__ == '__main__':
    # 测试通知功能
    sendkey = load_sendkey_from_file()
    if sendkey:
        notifier = ServerChanNotifier(sendkey)
        notifier.notify_signin_success("测试用户", "测试签到成功")
    else:
        print("请先设置sendkey.txt文件")