#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AcgFun 网站纯Cookie签到脚本
使用保存的Cookie进行登录验证和签到
"""

import requests
import logging
import time
import re
import argparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from wechat_notifier import ServerChanNotifier, load_sendkey_from_file
from credit_analyzer import CreditAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cookie_signin.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CookieSignin:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # 禁用SSL验证
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.base_url = 'https://acgfun.art'
        self.signin_url = 'https://acgfun.art/plugin.php?id=k_misign:sign'
        self.current_username = ''  # 存储当前用户名
        
        # 初始化Server酱通知器
        sendkey = load_sendkey_from_file()
        self.wechat_notifier = ServerChanNotifier(sendkey)
        
        # 初始化积分分析器
        self.credit_analyzer = CreditAnalyzer(self.session)
        
        # 禁用SSL警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def safe_request(self, method, url, **kwargs):
        """安全的网络请求，包含重试和错误处理"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.SSLError as e:
                logging.warning(f"SSL错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
            except requests.exceptions.ConnectionError as e:
                logging.warning(f"连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
            except requests.exceptions.Timeout as e:
                logging.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
            except Exception as e:
                logging.error(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
        
        return None

    def load_cookies_from_file(self, cookie_file):
        """从文件加载Cookie"""
        try:
            with open(cookie_file, 'r', encoding='utf-8') as f:
                cookie_string = f.read().strip()
            
            # 解析Cookie字符串
            cookies = {}
            for cookie in cookie_string.split('; '):
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    cookies[name] = value
            
            # 设置到session中
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='acgfun.art')
            
            logging.info(f"✅ Cookie加载成功，共加载了 {len(cookies)} 个cookies")
            return True
            
        except Exception as e:
            logging.error(f"❌ Cookie加载失败: {e}")
            return False

    def load_cookies_from_browser(self, browser_cookies):
        """从浏览器格式的Cookie字符串加载"""
        try:
            cookies = {}
            for cookie in browser_cookies.split('; '):
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    cookies[name] = value
            
            for name, value in cookies.items():
                self.session.cookies.set(name, value, domain='acgfun.art')
            
            logging.info(f"✅ Cookie加载成功，共加载了 {len(cookies)} 个cookies")
            return True
            
        except Exception as e:
            logging.error(f"❌ Cookie加载失败: {e}")
            return False

    def verify_login_status(self):
        """验证登录状态"""
        try:
            logging.info("🔍 正在验证登录状态...")
            
            # 访问个人中心页面来验证登录
            response = self.safe_request('GET', f'{self.base_url}/home.php?mod=space&do=profile')
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查是否包含登录用户信息
                if '个人资料' in response.text or 'profile' in response.text:
                    # 尝试提取用户名
                    username_element = soup.find('h2', class_='mbn')
                    if username_element:
                        username_text = username_element.get_text().strip()
                        # 提取用户名和UID
                        if '(' in username_text and ')' in username_text:
                            self.current_username = username_text.split('(')[0].strip()
                            logging.info(f"✅ 登录状态验证成功！当前用户: {username_text}")
                        else:
                            self.current_username = username_text
                            logging.info(f"✅ 登录状态验证成功！当前用户: {username_text}")
                        return True
                    else:
                        self.current_username = '未知用户'
                        logging.info("✅ 登录状态验证成功！")
                        return True
                
                # 如果上面没找到，检查是否需要登录
                if '登录' in response.text and '密码' in response.text:
                    logging.error("❌ 登录状态验证失败，Cookie已失效")
                    # 发送Cookie失效通知
                    self.wechat_notifier.notify_cookie_expired(self.current_username)
                    return False
                    
                # 默认认为登录成功
                self.current_username = '未知用户'
                logging.info("✅ 登录状态验证成功！")
                return True
            
            else:
                logging.error(f"❌ 访问个人中心失败: {response.status_code if response else 'No response'}")
                # 发送Cookie失效通知
                self.wechat_notifier.notify_cookie_expired(self.current_username)
                return False
                
        except Exception as e:
            logging.error(f"❌ 验证登录状态失败: {e}")
            # 发送Cookie失效通知
            self.wechat_notifier.notify_cookie_expired(self.current_username)
            return False

    def check_signin_status(self):
        """检查签到状态"""
        try:
            logging.info("🔍 正在检查签到状态...")
            
            response = self.safe_request('GET', self.signin_url)
            if not response:
                logging.error("❌ 无法访问签到页面")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = response.text
            
            # 优先检查明确的已签到标识
            if "您今天已经签到过了" in page_text:
                logging.info("✅ 今天已经签到过了")
                return "already_signed"
            
            # 检查是否有签到按钮（operation=qiandao）
            signin_button = soup.find('a', href=re.compile(r'operation=qiandao'))
            if signin_button:
                logging.info("📝 找到签到按钮，今天还没有签到")
                return "not_signed"
            
            # 检查是否包含“还没有签到”的明确文字
            if "您今天还没有签到" in page_text:
                logging.info("📝 今天还没有签到，可以进行签到")
                return "not_signed"
            
            # 如果没有签到按钮且没有明确的未签到文字，可能已经签到了
            if "签到" in page_text and "连续签到" in page_text:
                logging.info("✅ 检测到连续签到信息，可能已经签到")
                return "already_signed"
            
            # 默认情况
            logging.warning("⚠️ 无法确定签到状态")
            return "unknown"
                
        except Exception as e:
            logging.error(f"❌ 检查签到状态失败: {e}")
            return None

    def perform_signin(self):
        """执行签到操作"""
        try:
            logging.info("🎯 开始执行签到操作...")
            
            # 首先访问签到页面获取formhash和签到按钮
            response = self.safe_request('GET', self.signin_url)
            if not response:
                logging.error("❌ 无法访问签到页面")
                return False
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找签到按钮 - 这是唯一有效的签到方式
            signin_button = soup.find('a', href=re.compile(r'operation=qiandao'))
            if signin_button:
                signin_href = signin_button.get('href')
                if signin_href:
                    # 构建完整的签到URL
                    if signin_href.startswith('/'):
                        signin_url = urljoin(self.base_url, signin_href)
                    elif signin_href.startswith('plugin.php'):
                        signin_url = urljoin(self.base_url, signin_href)
                    else:
                        signin_url = signin_href
                    
                    logging.info(f"🔄 点击签到按钮: {signin_url}")
                    response = self.safe_request('GET', signin_url)
                    
                    if response:
                        signin_result = self._check_signin_result(response.text)
                        if signin_result:
                            logging.info("🎉 签到成功！")
                            return True
                        else:
                            logging.warning("⚠️ 签到响应检测未成功，进行最终验证...")
                            # 最后一次检查，避免误判
                            final_status = self.check_signin_status()
                            if final_status == "already_signed":
                                logging.info("✅ 最终验证：签到已完成")
                                return True
                            else:
                                logging.error("❌ 签到未成功")
                                return False
                    else:
                        logging.error("❌ 签到请求失败")
                        return False
            
            # 如果没有找到签到按钮，可能已经签到过了
            logging.warning("⚠️ 未找到签到按钮，可能已经签到过了")
            return False
            
        except Exception as e:
            logging.error(f"❌ 签到操作失败: {e}")
            return False

    def get_tiankonshi_info(self) -> str:
        """
        获取天空石信息
        
        Returns:
            str: 天空石信息字符串
        """
        try:
            logging.info("💰 正在获取天空石信息...")
            
            tiankonshi_count = self.credit_analyzer.get_tiankonhhi_count()
            if tiankonshi_count is not None:
                tiankonshi_info = f"当前天空石数量: {tiankonshi_count}"
                logging.info(f"✅ {tiankonshi_info}")
                return tiankonshi_info
            else:
                logging.warning("⚠️ 无法获取天空石信息")
                return "天空石信息获取失败"
                
        except Exception as e:
            logging.error(f"❌ 获取天空石信息失败: {e}")
            return "天空石信息获取失败"

    def _check_signin_result(self, response_text):
        """检查签到结果"""
        # 优先检查明确的成功关键词
        success_keywords = [
            "签到成功", "签到完成", "打卡成功", "签到奖励",
            "恭喜", "获得", "奖励", "连续签到", "今日签到",
            "积分", "天空石", "经验", "金币", "您获得了"
        ]
        
        for keyword in success_keywords:
            if keyword in response_text:
                logging.info(f"🎉 签到成功！检测到关键词: {keyword}")
                return True
        
        # 检查是否已经签到过
        if "您今天已经签到过了" in response_text or "今天已经签到" in response_text:
            logging.info("✅ 今天已经签到过了")
            return True
        
        # 检查页面跳转或状态变化（如果响应很短，可能是跳转页面）
        if len(response_text.strip()) < 100:
            logging.info("🔄 检测到页面跳转，可能签到成功，进行二次验证...")
            return self._verify_signin_by_status_check()
        
        # 如果响应中没有错误信息，且包含签到相关内容，可能成功
        error_keywords = ["失败", "错误", "异常", "请重试"]
        has_error = any(error in response_text for error in error_keywords)
        has_signin_content = any(word in response_text for word in ["签到", "每日", "连续"])
        
        if not has_error and has_signin_content:
            logging.info("🤔 未检测到错误信息且包含签到内容，进行二次验证...")
            return self._verify_signin_by_status_check()
        
        # 输出响应内容用于调试
        logging.debug(f"签到响应内容: {response_text[:500]}...")
        return False
    
    def _verify_signin_by_status_check(self):
        """通过检查签到状态来验证签到是否成功"""
        try:
            logging.info("🔍 进行签到状态二次验证...")
            time.sleep(2)  # 等待2秒让服务器处理
            
            # 重新检查签到状态
            signin_status = self.check_signin_status()
            if signin_status == "already_signed":
                logging.info("✅ 二次验证确认：签到已完成")
                return True
            else:
                logging.warning("⚠️ 二次验证：签到状态未变更")
                return False
                
        except Exception as e:
            logging.error(f"❌ 二次验证失败: {e}")
            # 如果二次验证失败，返回True避免误判
            return True

    def run(self, cookie_source, is_file=True):
        """运行签到流程"""
        try:
            logging.info("=" * 50)
            logging.info("🚀 开始Cookie签到流程...")
            
            # 加载Cookie
            if is_file:
                if not self.load_cookies_from_file(cookie_source):
                    self.wechat_notifier.notify_signin_failed(self.current_username, "Cookie加载失败")
                    return False
            else:
                if not self.load_cookies_from_browser(cookie_source):
                    self.wechat_notifier.notify_signin_failed(self.current_username, "Cookie加载失败")
                    return False
            
            # 验证登录状态
            if not self.verify_login_status():
                logging.error("❌ 登录验证失败，请检查Cookie是否有效")
                self.wechat_notifier.notify_cookie_expired(self.current_username)
                return False
            
            # 检查签到状态
            signin_status = self.check_signin_status()
            if signin_status == "already_signed":
                logging.info("✅ 今天已经签到，任务完成！")
                # 获取天空石信息并通知
                tiankonshi_info = self.get_tiankonshi_info()
                signin_detail = f"今日签到已完成\n{tiankonshi_info}"
                self.wechat_notifier.notify_signin_success(self.current_username, signin_detail)
                return True
            elif signin_status == "not_signed":
                # 执行签到
                if self.perform_signin():
                    logging.info("🎉 签到流程完成！")
                    
                    # 获取天空石信息
                    tiankonshi_info = self.get_tiankonshi_info()
                    signin_detail = f"今日签到任务已完成\n{tiankonshi_info}"
                    
                    self.wechat_notifier.notify_signin_success(self.current_username, signin_detail)
                    return True
                else:
                    logging.error("❌ 签到失败")
                    self.wechat_notifier.notify_signin_failed(self.current_username, "签到执行失败")
                    return False
            else:
                logging.warning("⚠️ 无法确定签到状态，尝试执行签到...")
                if self.perform_signin():
                    logging.info("🎉 签到流程完成！")
                    
                    # 获取天空石信息
                    tiankonshi_info = self.get_tiankonshi_info()
                    signin_detail = f"今日签到任务已完成\n{tiankonshi_info}"
                    
                    self.wechat_notifier.notify_signin_success(self.current_username, signin_detail)
                    return True
                else:
                    logging.error("❌ 签到失败")
                    self.wechat_notifier.notify_signin_failed(self.current_username, "签到执行失败")
                    return False
            
        except Exception as e:
            logging.error(f"❌ 签到流程失败: {e}")
            self.wechat_notifier.notify_signin_failed(self.current_username, f"签到流程异常: {str(e)}")
            return False
        finally:
            logging.info("=" * 50)

def main():
    parser = argparse.ArgumentParser(description='AcgFun Cookie签到脚本')
    parser.add_argument('--file', type=str, help='Cookie文件路径')
    parser.add_argument('--cookie', type=str, help='直接提供Cookie字符串')
    parser.add_argument('--clean-logs', action='store_true', help='签到后清理旧日志文件')
    
    args = parser.parse_args()
    
    if not args.file and not args.cookie:
        print("请提供Cookie文件路径 (--file) 或直接提供Cookie字符串 (--cookie)")
        return
    
    signin = CookieSignin()
    
    if args.file:
        success = signin.run(args.file, is_file=True)
    else:
        success = signin.run(args.cookie, is_file=False)
    
    # 清理旧日志文件（如果指定了参数）
    if args.clean_logs and success:
        try:
            from log_cleaner import LogCleaner
            log_cleaner = LogCleaner()
            if log_cleaner.run_cleanup():
                logging.info("🧹 日志清理完成")
            else:
                logging.warning("⚠️ 日志清理部分失败")
        except ImportError:
            logging.warning("⚠️ 日志清理模块未找到")
        except Exception as e:
            logging.warning(f"⚠️ 日志清理失败: {e}")
    
    if success:
        print("✅ 签到成功！")
    else:
        print("❌ 签到失败！")

if __name__ == '__main__':
    main()