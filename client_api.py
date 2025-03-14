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
from action import BBoxNotClickableException

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
            
            # 当前浏览器的代理状态
            time.sleep(8)
            img = screenshot_processor.screenshot()
            image_paths = [img]
            prompt = '''这是一张浏览器界面的截图，请判断页面显示代理（VPN）的状态是成功还是失败。判断参考：代理的成功依据是页面中有显示 IP（例如 IP：110.120.89.163 ）。 代理的失败依据是页面中会显示"代理失败"。如果页面中显示的内容有包含 ---.---.---.--- ，判断为代理失败。
            注意：您的响应应遵循以下格式：代理成功返回 {"agent": "success"}，代理失败返回 {"agent": "fail"}。请勿包含任何其他信息。'''
            
            res = action_handler.upload_multiple_images(image_paths, prompt)
            if not res:
                return None
            json_str = res['result']
            data = json.loads(json_str)
            agent_state = data.get("agent")
            logger.info(f'代理状态：{agent_state}')
            if agent_state == "fail":
                return jsonify({
                    'status': 'error',
                    'message': "代理失败"
                }), 500
                

            # 当前浏览器打开了几个标签页
            # success, result, status_code = screenshot_processor.process_screenshot()
            # image_paths = [result["processed_image"]]
            # prompt = '''这是一张浏览器界面的截图，请判断图片最上面的标题栏（有"+"符号的那栏）有几个序号标注。
            # 注意：你的响应应遵循以下格式：{"tab_count": n}, n 是数字。例如：{"tab_count": 5}，其中 5 表示总共有5个序号标注。请勿包含任何其他信息。
            # '''
            
            # img = screenshot_processor.screenshot()
            # image_paths = [img]
            # # （注意：要忽略标题中大写或小写"x"字母）
            # prompt = '''这是一张浏览器界面的截图，请判断浏览器打开了几个标签页。
            # 如何得出有多少个标签，判断方法如下：
            #     根据浏览器的标题栏总里共有几个 "x"形状的关闭按钮，那么就有几个标签
                
            # 注意：您的响应应遵循以下格式：{"tab_count": n}, n 是数字。例如：{"tab_count": 5}，其中 5 表示打开了5个标签。请勿包含任何其他信息。'''
            #  - 方法二： 根据浏览器的标题栏里的 "+" 字符前的标题来判断有多少个标签。有几个标题，就有几个标签。如果标题只是单独一个特殊符号的是不能计算在内的，因为它不是标签，而是功能按钮
            # 请结合方法一与方法二判断出有几个标签。   
            
            # res = action_handler.upload_multiple_images(image_paths, prompt)
            # if not res:
            #     return None
            # json_str = res['result']
            # data = json.loads(json_str)
            # tab_count = data.get("tab_count") - 2
            # logger.info(f'当前打开了{tab_count}个标签页')
            
            tab_count = 1
            # 根据有几个标签页做输入 walmart 地址
            # 打开新标签
            # 输入  www.walmart.com
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
        if isinstance(e, BBoxNotClickableException):
            return jsonify({
                'code': -100,
                'status': 'error',
                'action': action,
                'message': f'bbox找不到或不可点击: action={action} --- {str(e)}'
            }), 500

        return jsonify({
            'code': 0,
            'status': 'error',
            'action': action,
            'message': f'流程处理失败: action={action} --- {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
