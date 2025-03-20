from flask import Flask, jsonify, request
import os
import time
import json
from datetime import datetime
from browser import Browser
from mouse_controller import MouseController  # 添加导入
from action import Action  # 添加Action导入
from utils.api_client import APIClient
from screenshot_processor import ScreenshotProcessor
from pywinauto import Desktop
from utils.logger import get_logger
import pyautogui
from action import BBoxNotClickableException, OpenPageFail

logger = get_logger(__name__)
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
    'check_is_walmart_plus': lambda handler, account_info: handler.check_is_walmart_plus(account_info),
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
    'click_add_address': lambda handler, account_info: handler.click_add_address(account_info),
    'fill_address_form': lambda handler, account_info: handler.fill_address_form(account_info),
    'fill_wallet_form': lambda handler, account_info: handler.fill_wallet_form(account_info),
    'after_create_address_enter_wallet': lambda handler, account_info: handler.after_create_address_enter_wallet(account_info),
    'start_fress_30_day_trial': lambda handler: handler.start_fress_30_day_trial(),
    'join_walmart_plus_result': lambda handler, account_info: handler.join_walmart_plus_result(account_info),
    'logging': lambda handler, account_info: handler.logging(account_info),
}

@app.route('/start_browser', methods=['POST'])
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

            browser.close_browser(account_info['ads_id'])
            browser.start_browser()
            
            # success, result, status_code = screenshot_processor.process_screenshot()
            # if status_code == 200:
            #     bbox = []
            #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
            #              第二张图片上这些序号都被彩色方框包围，方框外的就不是数字所属的部分。
            #              请在第二张图片找出浏览器最大化的操作按钮。
            #              注意：您的响应应遵循以下格式：{"btn": 3}，3表示序号。请勿包含任何其他信息。'''
            #     number = action_handler.process_image_with_prompt(prompt=prompt, result=result, expected_key="btn")
                
            #     # 从 result['parsed_content'] 中遍历找出第 number 个的数据
            #     if action_handler._click_element_by_number(number, result['parsed_content']):
            #         bbox = result['parsed_content'][number]
            #     else:
            #         raise Exception(f"寻找浏览器最大化按钮 -- 获取 number 失败")
            # else:
            #     raise  Exception(f"寻找浏览器最大化按钮报错: {result}")
            
            # mouse_controller.click_bbox(bbox)
            
            windows = Desktop(backend='uia').windows()
            target_title = account_info['amz_name']
            target_window = None
            
            for w in windows:
                if target_title.lower() in w.window_text().lower():
                    target_window = w
                    break
                
            if target_window:
                target_window.maximize()
                logger.info(f"窗口 '{target_title}' 已最大化")
                time.sleep(3.5)
            else:
                logger.error(f"未找到标题包含 '{target_title}' 的窗口")
                return jsonify({
                    'status': 'fail',
                    'message': f"未找到标题包含 '{target_title}' 的窗口"
                }), 500
            
            for i in range(5):
            # 当前浏览器的代理状态
                time.sleep(3.5)
                img = screenshot_processor.screenshot()
                image_paths = [img]
                prompt = '''分析这张浏览器截图，判断代理状态：
                1. 代理成功标志：页面上蓝色区域显示有效网络IP地址。（IP地址是由于数字与.组成的，所以有效网络IP地址一定要包含有数字）
                2. 代理失败标志：页面显示"代理失败"或页面蓝色区域包含"---.---.---.---"

                注意：您的响应应遵循以下格式：
                {"agent": "success"} - 代理成功
                {"agent": "fail"} - 代理失败
                请勿包含任何其他信息。'''
                
                res = action_handler.upload_multiple_images(image_paths, prompt)
                if not res:
                    logger.error(f'res --- {res}')
                    return None
                json_str = res['result']
                data = json.loads(json_str)
                agent_state = data.get("agent")
                logger.info(f'代理状态：{agent_state}')
                if agent_state == "success":
                    break


            if agent_state == "fail":
                return jsonify({
                    'status': 'error',
                    'message': "代理失败"
                }), 500
            
            tab_count = 1
            # 根据有几个标签页做输入 walmart 地址
            if tab_count == 1:
                add_btn_bbox = [0.10888566076755524, 0.004173490684479475, 0.11842383444309235, 0.02574099972844124]
            elif tab_count == 2:
                add_btn_bbox =  []
            elif tab_count == 3:
                add_btn_bbox =  []
            elif tab_count == 4:
                add_btn_bbox =  []
            elif tab_count == 5:
                add_btn_bbox =  []
            else:
                pass
            mouse_controller.click_bbox(add_btn_bbox)
            url_input_bbox = [0.03242187574505806, 0.03333333507180214, 0.25507813692092896, 0.05694444477558136]
            mouse_controller.click_bbox(url_input_bbox)
            # 清空现有内容
            pyautogui.hotkey('ctrl', 'a')  # 全选现有文本
            pyautogui.press('delete')      # 删除选中内容
            time.sleep(0.2)                # 短暂等待清空完成
            # 输入文本
            mouse_controller.type_text(YAHOO_WALMART_SEARCH)
            time.sleep(0.2)  # 等待输入完成
            pyautogui.press('enter')

            
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
            if action in ["fill_address_form", "fill_wallet_form", "logging", "click_add_address", "join_walmart_plus_result", "check_is_walmart_plus", "after_create_address_enter_wallet"]:
                re = handler(action_handler, account_info)  # Pass account_info to the handler
            else:
                re = handler(action_handler)
        else:
            logger.error(f"未知的action类型: {action}")
            re = {'success': False, 'message': f'未知的action类型: {action}'}

        return jsonify({
            'code': 1,
            'status': 'success',
            'action': action,
            'res': re
        }), 200

    except Exception as e:
        if isinstance(e, BBoxNotClickableException):
            return jsonify({
                'code': -100,
                'status': 'error',
                'action': action,
                'message': f'bbox找不到或不可点击: action={action} --- {str(e)}'
            }), 500
        
        if isinstance(e, OpenPageFail):
            return jsonify({
                'code': -602,
                'status': 'error',
                'action': action,
                'message': f'网页打开失败: action={action} --- {str(e)}'
            }), 500

        return jsonify({
            'code': 0,
            'status': 'error',
            'action': action,
            'message': f'流程处理失败: action={action} --- {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
