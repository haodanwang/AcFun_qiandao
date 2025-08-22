#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AcgFun 签到状态验证脚本
验证当前的签到状态
"""

import requests
import logging
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SigninVerifier:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        self.signin_url = 'https://acgfun.art/plugin.php?id=k_misign:sign'
        
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def load_cookies_from_file(self, cookie_file):
        """从文件加载Cookie"""
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_string = f.read().strip()
            
            cookies = {}
            for cookie in cookie_string.split('; '):
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    cookies[name] = value
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='acgfun.art')
            
            logging.info(f"✅ Cookie加载成功")
            return True
            
        except Exception as e:
            logging.error(f"❌ Cookie加载失败: {e}")
            return False

    def check_signin_status(self):
        """检查签到状态"""
        try:
            logging.info("🔍 正在检查当前签到状态...")
            
            response = self.session.get(self.signin_url, timeout=30)
            if response.status_code != 200:
                logging.error(f"❌ 访问签到页面失败: {response.status_code}")
                return False
            
            # 检查页面内容
            if "您今天已经签到过了" in response.text:
                logging.info("✅ 验证成功：今天已经签到过了！")
                return True
            elif "您今天还没有签到" in response.text:
                logging.warning("⚠️ 显示还没有签到")
                return False
            else:
                # 更详细的分析
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找签到相关的文本
                page_text = response.text
                if "已签到" in page_text or "签到成功" in page_text:
                    logging.info("✅ 验证成功：检测到已签到状态！")
                    return True
                elif "签到" in page_text and "未签到" not in page_text:
                    # 如果有签到相关内容但没有明确的未签到标识
                    logging.info("🤔 页面包含签到相关内容，可能已签到")
                    return True
                else:
                    logging.warning("⚠️ 无法明确确定签到状态")
                    return False
                
        except Exception as e:
            logging.error(f"❌ 检查签到状态失败: {e}")
            return False

def main():
    verifier = SigninVerifier()
    
    # 加载Cookie
    if not verifier.load_cookies_from_file('cookies.txt'):
        print("❌ Cookie加载失败")
        return
    
    # 检查签到状态
    if verifier.check_signin_status():
        print("🎉 签到状态验证：已签到")
    else:
        print("❌ 签到状态验证：未签到")

if __name__ == '__main__':
    main()