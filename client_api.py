from flask import Flask, jsonify, request
import os
import time
from datetime import datetime
from browser import Browser
from mouse_controller import MouseController  # 添加导入
from action import Action  # 添加Action导入
from utils.api_client import APIClient
from screenshot_processor import ScreenshotProcessor

app = Flask(__name__)

# 初始化各种实例
browser = Browser()
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
    'start_fress_30_day_trial': lambda handler: handler.start_fress_30_day_trial(),
    'join_walmart_plus_result': lambda handler: handler.join_walmart_plus_result(),
}

@app.route('/start', methods=['POST'])
def start_browser():
    try:
        # 获取 walmart帐号信息
        try:
            account_info = request.json.get('account_info')  # 从 POST 参数中获取 account_info
            
            # 使用API返回的账户信息，确保 password 为字符串
            browser_data = {
                'ads_id': account_info['ads_id'],
                'email': account_info['email'],
                'password': account_info['password'] or '',  # 如果是 None 则使用空字符串
                'account_password': account_info['account_password']
            }
            
            # ads.start_browser(browser_data)
            browser.init_user_info(browser_data)
            
            # YAHOO_WALMART_SEARCH = 'https://www.google.com/search?q=walmart'
            YAHOO_WALMART_SEARCH = 'https://www.walmart.com' # /wallet
            #ads.driver.execute("newWindow", {'url': 'https://www.google.com/search?p=walmart'})

            browser.start_browser()
            
            
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
    
@app.route('/close_browser', methods=['POST'])
def close_browser():
    try:
        account_info = request.json.get('account_info')  # 从 POST 参数中获取 account_info
        browser.close_browser(account_info['ads_id'])
        return jsonify({
                'status': 'success',
                'message': '关闭浏览器成功'
            }), 200
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'关闭浏览器失败: {str(e)}'
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
            'code': 1,
            'status': 'success',
            'action': action,
            'res': re
        }), 200

    except Exception as e:
        return jsonify({
            'code': 0,
            'status': 'error',
            'action': action,
            'message': f'截图或处理失败: action={action} --- {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
