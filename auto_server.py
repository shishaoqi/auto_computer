# 所有步骤集中地
import requests
from dotenv import load_dotenv
import os
import time
from utils.logger import get_logger
from utils.api_client import APIClient
from status import Status
import json
import signal
import sys
import atexit

# Load environment variables from .env file
load_dotenv()
logger = get_logger(__name__)

# Global variable to track unconsumed items
unconsumed_items = []

def save_unconsumed_items():
    """Save any unconsumed items to a file when the program exits"""
    if unconsumed_items:
        try:
            with open('unconsumed_items.json', 'w') as f:
                json.dump(unconsumed_items, f)
            logger.info(f"Saved {len(unconsumed_items)} unconsumed items to file")
        except Exception as e:
            logger.error(f"Failed to save unconsumed items: {e}")

def load_unconsumed_items():
    """Load any previously unconsumed items from file"""
    try:
        if os.path.exists('unconsumed_items.json'):
            with open('unconsumed_items.json', 'r') as f:
                items = json.load(f)
            logger.info(f"Loaded {len(items)} unconsumed items from file")
            # Remove the file after loading
            os.remove('unconsumed_items.json')
            return items
    except Exception as e:
        logger.error(f"Failed to load unconsumed items: {e}")
    return []

def handle_exit(signum=None, frame=None):
    """Handle program exit gracefully"""
    logger.info("Program is exiting, saving unconsumed items...")
    save_unconsumed_items()
    sys.exit(0)

# Register the exit handler
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
atexit.register(save_unconsumed_items)

def process(account_info, action:str = "", start_browser:bool=False):
    start_time = time.time()  # Start timing

    if start_browser:
        result = call_api(account_info, "start_browser") # 启动 Ads 浏览器
        logger.info(f'call_api -- start_browser RESPONSE: {result}')
        if result == 'connect client fail':
            logger.error('客户端未启动 (或可能客户依赖的服务连接不正常） ~ ~ ~')
            return
        
        if result.get("status") == "error":
            msg = result.get("message")
            if msg == "代理失败":
                post_member_operate_res(account_info, Status.STATUS_AGENT_FAIL)
                return {'code': -601, 'message': '代理失败', 'status': 'error', 'action': ''}
            
    # 检测是否已经开启 Walmart+
    res = call_action_api(action="check_is_walmart_plus")
    if isinstance(res, dict) and res.get('res') == 1:
        return {"status": "success", "action": ""}
    
    # Start from the specified action
    actions_sequence = [
        # "find_walmart",
        "click_account_btn",
        # "enter_account",
        "click_account_setting",
        "click_address",
        "click_add_address"
    ]

    has_address = False
    has_wallet = False
    if action == "":
        action = "click_account_btn"

    # Find the index of the specified action in the sequence
    try:
        start_index = actions_sequence.index(action)
    except ValueError:
        # If action is not in the sequence, it might be one of the form filling actions
        # which will be handled in the next sections
        start_index = len(actions_sequence)

    # Execute actions starting from the specified one
    for i in range(start_index, len(actions_sequence)):
        current_action = actions_sequence[i]
        logger.info(f"Executing action: {current_action}")
        
        # Add appropriate sleep times between actions
        time.sleep(3.5)
        if current_action in ["click_add_address"]:
            res = call_action_api(action=current_action, account_info=account_info)
            if res.get('res') == 205:
                has_address = True
        else:
            res = call_action_api(action=current_action)
        logger.info(f'call_action_api RESPONSE: {res}')
        if res is None or (isinstance(res, dict) and res.get('code') != 1):
            logger.info(f'call_capture_api {current_action} 出错， res = {res}')
            # 如果 action 是 click_account_setting，则检查下是不是未登录
            # 未登录，下一步就进行登录。登录流程走完，就回归到主流程
            if res.get("action") == "click_account_setting":
                logging_res = call_action_api(action="logging", account_info=account_info)
                logger.info(f'logging_res == {logging_res}')
                res = logging_res.get("res")
                if res:
                    logging = res.get("logging")
                    logger.info(f"logging status: {logging}")
                    if logging == 0:
                        return {'code': -603, 'message': '帐号未登录', 'status': 'error', 'action': ''}
                else:
                    logger.info("异常-----")

            return {"status": "continue", "action": current_action}
        elif (isinstance(res, dict) and res.get('code') == -602):
            logger.info(f'call_capture_api {current_action} 出错， res = {res}')
            return {"status": "continue", "action": current_action}

    # 完成导航步骤后，进入表单填写
    if action in actions_sequence:
        action = "fill_address_form"
        
    if action == "fill_address_form":
        if has_address:
            action = "fill_wallet_form"
        else:
            res = call_action_api(action="fill_address_form", account_info=account_info)
            # 检查 res 是否为字典，并检查 'res' 键的值
            if (isinstance(res, dict) and res.get('res') != 1):
                return {"status": "fail", "action": "fill_address_form"}
            elif (isinstance(res, dict) and res.get('code') == 0):
                logger.error('fill_address_form error')
                pass
            action = "fill_wallet_form"

    if action == "fill_wallet_form":
        # 如果添加地址成功，则进行创建银行卡
        res = call_action_api(action="after_create_address_enter_wallet", account_info=account_info)
        if (isinstance(res, dict) and res.get('res') == 1):
            res = call_action_api(action="fill_wallet_form", account_info=account_info)
            if isinstance(res, dict) and res.get('res') != 1:
                return {"status": "fail", "action": "fill_wallet_form"}
        elif (isinstance(res, dict) and res.get('res') == 206):
            has_wallet = True
        elif (isinstance(res, dict) and res.get('code') == -100):
            logger.error(res.get('message'))
            # 找不到添加卡的链接
            if res.get('message') == "bbox找不到或不可点击: action=after_create_address_enter_wallet --- after_create_address_enter_wallet card_bbox 不可点击":
                logger.info('找不到卡')

        action = "start_fress_30_day_trial"
    
    if action == "start_fress_30_day_trial":
        res = call_action_api(action="start_fress_30_day_trial")
        if (isinstance(res, dict) and res.get('res') != 1):
            return {"status": "fail", "action": "start_fress_30_day_trial"}
        elif (isinstance(res, dict) and res.get('code') == 0):
            pass

    # 视觉模型确认是否开通会员成功
    re = call_action_api(action="join_walmart_plus_result")
    is_join = 0
    if isinstance(re, dict):
        is_join = re.get('res')
        logger.info(f'join walmart+ -------- : {is_join}')
        if is_join != "success":
            return {'code': -604, 'message': '最后开通 Walmart+ 失败', 'status': 'error', 'action': ''}
    
    # Calculate and log total execution time
    execution_time = time.time() - start_time
    logger.info(f"--------- Total execution time: {execution_time:.2f} seconds")

    # 最后 -- 关闭浏览器
    re = call_api(account_info, "close_browser")
    logger.info(f'close_browser: {re}')

    # 添加默认返回值，确保函数不会返回 None
    return {"status": "success", "action": ""}

# 第一步：打开浏览器（已进入到搜索 walmart 结果的页）
def call_api(account_info, api_name: str):
    # 做为服务的文件是 client_api.py (当要查看代码时，请跳到 client_api.py)
    url = os.getenv('START_API_URL', 'http://localhost:5000') + '/' + api_name  # Default fallback if not set in .env
    
    try:
        response = requests.post(url, json={"account_info": account_info})
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info("Success: %s", result['message'])
            return result
        else:
            result = response.json()
            logger.info("Error message: %s", result['message'])
            return result
            
    except requests.exceptions.RequestException as e:
        logger.info("Request failed: %s", str(e))
        # 请查看视觉模型服务是否正常
        return 'connect client fail'



def call_action_api(action, account_info={}):
    """
    Call the capture API with specified action
    """
    # 做为服务的文件是 client_api.py (当要查看代码时，请跳到 client_api.py)
    url = os.getenv('CAPTURE_API_URL', 'http://localhost:5000') + '/capture'  # Default fallback if not set in .env
    
    # Prepare data payload for POST request
    data = {"action": action}
    if account_info:  # Only add account_info if it's not empty
        data["account_info"] = account_info
    
    try:
        response = requests.post(url, json=data)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info("Capture API Success for action '%s': %s", action, result)
            return result
        else:
            result = response.json()
            logger.info("Error message: ------  %s", result)
            return result
            
    except requests.exceptions.RequestException as e:
        logger.info("Capture API request failed: %s", str(e))
        return None
    
### 如果你不知道要如何做 或 没有可以参考的指令，那么你发起钉钉通知

def post_member_operate_res(account_info, status: int=0):
    url = "https://assist.weinpay.com/api/PyHandle/memberOperateRes"
    data_form = {
        "timestamp": 1722579064,
        "signed": "8FD39EABE64DC7E6F56953FD8EE5B31C",
        "task_id": account_info["task_id"],
        "code": 0,
        "status": status
    }
    
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = requests.post(url, json=data_form)
            if response.status_code == 200:
                logger.info("POST request successful: %s", response.json())
                return response.json()  # Return the successful response
            else:
                logger.info("POST request failed: %d", response.status_code)
        except requests.exceptions.RequestException as e:
            logger.info("POST request error: %s", str(e))
        
        time.sleep(3)  # Optional: wait before retrying

    return None  # Return None if all attempts fail


if __name__ == '__main__':
    team = os.getenv('TEAM_NAME', 'wining')  # Read team name from .env, default to 'wining'

    api_client = APIClient()
    actions_sequence = [
        # "find_walmart",
        "click_account_btn",
        # "enter_account",
        "click_account_setting",
        "click_address",
        "click_add_address"
    ]

    # Load any previously unconsumed items
    unconsumed_items = load_unconsumed_items()
    
    # Retry fetching the member operate list if it's empty
    while True:
        # Process any unconsumed items first
        if unconsumed_items:
            logger.info(f"Processing {len(unconsumed_items)} previously unconsumed items")
            list_to_process = unconsumed_items
            unconsumed_items = []  # Clear the list as we're about to process these items
        else:
            # Fetch new items from API
            result = api_client.get_member_operate_list(page=1, limit=5, team=team)
            list_to_process = result['data']['list']
            # list_to_process = list_to_process[3:]
            
            if len(list_to_process) == 0:
                logger.info("List is empty, retrying in 15 seconds...")
                time.sleep(15)  # Wait for 15 seconds before retrying
                continue

        # Store all items as unconsumed initially
        unconsumed_items = list_to_process.copy()
        
        # Process each item
        for account_info in list_to_process:
            logger.info(f'执行开通Walmart+, walmart 帐户信息 ------ {account_info}') # walmart 帐户信息
            
            res = {"status": "fail", "action": ""}
            start_browser = True
            for i in range(3):  # Retry up to 3 times
                status = 0 #给 PHP 服务记录的状态
                next_action = res.get("action", "") if res is not None else ""

                # fill_address_form 动作前失败的动作都重新从 click_account_btn 开始
                if next_action in actions_sequence:
                    next_action = "click_account_btn"

                res = process(account_info, next_action, start_browser)
                logger.info(f'process return res ====== {res}')
                if isinstance(res, dict) and res.get("status") == "success":
                    status = Status.STATUS_SUCCEED
                    break  # Exit the loop if successful
                elif isinstance(res, dict) and res.get("status") == "error":
                    if res.get("code") == -601:
                        status = Status.STATUS_AGENT_FAIL
                        start_browser = True
                    elif res.get("code") == -603:
                        status = Status.STATUS_LOGOUT
                        start_browser = False
                        break
                    elif res.get("code") == -604:
                        status = Status.STATUS_MEMBERSHIP_CREATE_UNKNOW_ERROR
                        start_browser = False
                        break
                elif isinstance(res, dict) and res.get("status") == "continue":
                    logger.info("process failed, retried %s times:  Ads: %s", i+1, account_info['ads_id'])
                    start_browser = True
                else:
                    logger.info("------------- process failed %s:  Ads: %s", i+1, account_info['ads_id'])
                    # 置空，让其重新开始
                    res['action'] = ""
                    start_browser = True

            # Post the result to the server
            result = post_member_operate_res(account_info, status)
            
            # Mark this item as consumed by removing it from unconsumed_items
            if account_info in unconsumed_items:
                unconsumed_items.remove(account_info)
                logger.info(f"Marked item with ads_id {account_info.get('ads_id')} as consumed")




        

