import base64
import io
from flask import Flask, jsonify, request
from PIL import ImageGrab
from PIL import Image
import os
import time
import requests
from datetime import datetime
from Ads import Ads  # 添加Ads导入
from mouse_controller import MouseController  # 添加导入
from action import Action  # 添加Action导入
from utils.api_client import APIClient
from screenshot_processor import ScreenshotProcessor

app = Flask(__name__)

# 初始化各种实例
ads = Ads()
mouse_controller = MouseController()
api_client = APIClient()
screenshot_processor = ScreenshotProcessor()
action_handler = Action(screenshot_processor, mouse_controller)

# 确保screenshots和detecting文件夹存在
for folder in ['screenshots', 'detecting']:
    if not os.path.exists(folder):
        os.makedirs(folder)

# 在文件开头添加 action 映射字典 ---- 以下方法实现在  action.py 文件中
ACTION_HANDLERS = {
    'click_account_btn': lambda handler: handler.click_account_btn(),
    'bind_address': lambda handler: handler.bind_address(),
    'create_bankCard': lambda handler: handler.create_bankCard(),
    'login': lambda handler: handler.login(),
    'find_walmart': lambda handler: handler.find_walmart(),
    'is_walmart_page': lambda handler: handler.is_walmart_page(),
    'enter_account': lambda handler: handler.enter_account(),
    'click_account_setting': lambda handler: handler.click_account_setting(),
    'click_address': lambda handler: handler.click_address(),
    'click_wallet': lambda handler: handler.click_wallet(),
    'click_add_address': lambda handler: handler.click_add_address(),
    'fill_address_form': lambda handler, account_info: handler.fill_address_form(account_info),
    'fill_wallet_form': lambda handler, account_info: handler.fill_wallet_form(account_info),
    'after_create_address_enter_wallet': lambda handler: handler.after_create_address_enter_wallet(),
}

@app.route('/start', methods=['POST'])
def start_browser():
    try:
        # 获取 walmart帐号信息
        try:
            result = api_client.get_member_operate_list()
            # walmart 帐户信息
            account_info = result['data']['list'][0]
            print(account_info)
            
            # 使用API返回的账户信息，确保 password 为字符串
            browser_data = {
                'ads_id': account_info['ads_id'],
                'email': account_info['email'],
                'password': account_info['password'] or '',  # 如果是 None 则使用空字符串
                'account_password': account_info['account_password']
            }
            
            ads.start_browser(browser_data)
            
            if not ads.driver:
                return jsonify({
                    'status': 'error',
                    'message': '浏览器启动失败: driver is None'
                }), 500
            
            YAHOO_WALMART_SEARCH = 'https://www.google.com/search?q=walmart'
            YAHOO_WALMART_SEARCH = 'https://www.walmart.com/wallet'
            #ads.driver.execute("newWindow", {'url': 'https://www.google.com/search?p=walmart'})
            # 记录当前窗口句柄
            original_handles = ads.driver.window_handles
            
            # 打开新窗口
            ads.driver.execute("newWindow", {'url': YAHOO_WALMART_SEARCH})
            
            # 等待新窗口出现并获取新窗口句柄
            timeout = 10
            new_handle = None
            start_time = time.time()
            while time.time() - start_time < timeout:
                current_handles = ads.driver.window_handles
                if len(current_handles) > len(original_handles):
                    new_handle = [h for h in current_handles if h not in original_handles][0]
                    break
                time.sleep(0.5)
            
            if not new_handle:
                raise Exception("新窗口未能成功打开")
            
            # 切换到新窗口
            ads.driver.switch_to.window(new_handle)
            
            # 确保页面加载完成
            ads.driver.get(YAHOO_WALMART_SEARCH)
            
            return jsonify({
                'status': 'success',
                'message': '浏览器启动成功',
                'account_info': account_info
            }), 200
            
        except Exception as e:
            print(f"API request failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'获取账户信息失败: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'浏览器启动失败: {str(e)}'
        }), 500

@app.route('/capture', methods=['POST'])
def capture_screen():
    try:
        action = request.json.get('action')
        account_info = request.json.get('account_info')  # Added to retrieve account_info
        
        # 使用字典获取对应的处理函数
        handler = ACTION_HANDLERS.get(action)
        if handler:
            if action in ["fill_address_form", "fill_wallet_form"]:
                re = handler(action_handler, account_info)  # Pass account_info to the handler
            else:
                re = handler(action_handler)
        else:
            print(f"未知的action类型: {action}")
            re = {'success': False, 'message': f'未知的action类型: {action}'}

        return jsonify({
            'status': 'success',
            'res': re
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'截图或处理失败: action={action} --- {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
