#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AcgFun天空石积分分析脚本
获取用户当前的天空石数量
"""

import requests
import logging
import re
from bs4 import BeautifulSoup

class CreditAnalyzer:
    def __init__(self, session=None):
        """
        初始化积分分析器
        
        Args:
            session: requests会话对象，如果提供则使用现有session
        """
        self.session = session or requests.Session()
        self.session.verify = False
        
        # 设置请求头
        if not session:
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
        
        self.credit_url = 'https://acgfun.art/home.php?mod=spacecp&ac=credit&showcredit=1'
        
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
            except Exception as e:
                logging.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    continue
                raise
        
        return None

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
            
            logging.info(f"✅ Cookie加载成功，共加载了 {len(cookies)} 个cookies")
            return True
            
        except Exception as e:
            logging.error(f"❌ Cookie加载失败: {e}")
            return False

    def get_credit_info(self):
        """
        获取积分信息
        
        Returns:
            Dict: 积分信息字典，包含天空石等积分数据
        """
        try:
            logging.info("🔍 正在获取积分信息...")
            
            response = self.safe_request('GET', self.credit_url)
            if not response:
                logging.error("❌ 无法访问积分页面")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 分析页面结构，寻找积分信息
            credit_info = {}
            
            # 专门查找class="xi1 cl"的元素
            xi1_elements = soup.find_all(class_="xi1 cl")
            logging.info(f"找到 {len(xi1_elements)} 个 class='xi1 cl' 元素")
            
            for element in xi1_elements:
                element_text = element.get_text().strip()
                logging.info(f"xi1 cl 元素内容: {element_text}")
                
                # 在这个元素中查找天空石相关信息
                if '天空石' in element_text:
                    # 提取数字
                    numbers = re.findall(r'\d+', element_text)
                    if numbers:
                        # 通常第一个数字是当前数量
                        credit_info['天空石'] = int(numbers[0])
                        logging.info(f"✅ 在 xi1 cl 元素中找到天空石数量: {numbers[0]}")
                        
                        # 如果有多个数字，可能第二个是今日获得
                        if len(numbers) > 1:
                            credit_info['天空石_今日获得'] = int(numbers[1])
                            logging.info(f"✅ 天空石今日获得: {numbers[1]}")
                        break
            
            # 如果在xi1 cl中没找到，尝试查找其周围的元素
            if '天空石' not in credit_info and xi1_elements:
                for xi1_element in xi1_elements:
                    # 查找父元素
                    parent = xi1_element.parent
                    if parent:
                        parent_text = parent.get_text()
                        if '天空石' in parent_text:
                            numbers = re.findall(r'\d+', parent_text)
                            if numbers:
                                credit_info['天空石'] = int(numbers[0])
                                logging.info(f"✅ 在 xi1 cl 父元素中找到天空石数量: {numbers[0]}")
                                break
                    
                    # 查找兄弟元素
                    siblings = xi1_element.find_next_siblings()
                    for sibling in siblings:
                        sibling_text = sibling.get_text()
                        if '天空石' in sibling_text:
                            numbers = re.findall(r'\d+', sibling_text)
                            if numbers:
                                credit_info['天空石'] = int(numbers[0])
                                logging.info(f"✅ 在 xi1 cl 兄弟元素中找到天空石数量: {numbers[0]}")
                                break
                    if '天空石' in credit_info:
                        break
            
            # 备用方法：在整个页面中查找包含天空石的元素
            if '天空石' not in credit_info:
                logging.info("在 xi1 cl 元素中未找到天空石，尝试其他方法...")
                
                # 查找所有包含"天空石"的元素
                tiankonoshi_elements = soup.find_all(string=re.compile(r'天空石'))
                for text_node in tiankonoshi_elements:
                    if text_node.parent:
                        # 获取包含天空石文本的元素
                        element = text_node.parent
                        element_text = element.get_text()
                        
                        # 在这个元素及其周围查找数字
                        numbers = re.findall(r'\d+', element_text)
                        if numbers:
                            credit_info['天空石'] = int(numbers[0])
                            logging.info(f"✅ 通过文本搜索找到天空石数量: {numbers[0]}")
                            break
                        
                        # 查找相邻的元素
                        next_sibling = element.find_next_sibling()
                        if next_sibling:
                            sibling_numbers = re.findall(r'\d+', next_sibling.get_text())
                            if sibling_numbers:
                                credit_info['天空石'] = int(sibling_numbers[0])
                                logging.info(f"✅ 在天空石元素的下一个兄弟元素中找到数量: {sibling_numbers[0]}")
                                break
            
            if credit_info:
                logging.info(f"✅ 积分信息获取成功: {credit_info}")
                return credit_info
            else:
                logging.warning("⚠️ 未找到任何积分信息")
                # 输出页面结构用于调试
                logging.info("页面中包含的关键词：")
                if '天空石' in response.text:
                    logging.info("✓ 页面包含'天空石'")
                else:
                    logging.warning("✗ 页面不包含'天空石'")
                return None
                
        except Exception as e:
            logging.error(f"❌ 获取积分信息失败: {e}")
            return None

    def get_tiankonhhi_count(self):
        """
        专门获取天空石数量
        
        Returns:
            int: 天空石数量，失败返回None
        """
        credit_info = self.get_credit_info()
        if credit_info and '天空石' in credit_info:
            return credit_info['天空石']
        return None

def main():
    """测试函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AcgFun积分分析工具')
    parser.add_argument('--cookies', type=str, default='config/cookies.txt', help='Cookie文件路径')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建分析器
    analyzer = CreditAnalyzer()
    
    # 加载Cookie
    if not analyzer.load_cookies_from_file(args.cookies):
        print("❌ Cookie加载失败")
        return
    
    # 获取积分信息
    credit_info = analyzer.get_credit_info()
    if credit_info:
        print("🎉 积分信息获取成功：")
        for key, value in credit_info.items():
            print(f"   {key}: {value}")
    else:
        print("❌ 积分信息获取失败")

if __name__ == '__main__':
    main()