# 所有步骤集中地
import requests
from dotenv import load_dotenv
import os
import time
from utils.logger import get_logger
from utils.api_client import APIClient

# Load environment variables from .env file
load_dotenv()
logger = get_logger(__name__)

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
            logger.info("Error: %d", response.status_code)
            logger.info("Error message: %s", response.json()['message'])
            return None
            
    except requests.exceptions.RequestException as e:
        logger.info("Request failed: %s", str(e))
        return 'connect client fail'

# find_walmart
# 第二步：截图分辨, 找到 walmart, 打开它
### 异常：找不到，取截图，询问当前是什么情况，有什么处理办法。(例如有弹窗，关闭弹窗)
def call_capture_api(action, account_info={}):
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
            # logger.info("Error: %d", response.status_code)
            logger.info("Error message: %s", result)
            return result
            
    except requests.exceptions.RequestException as e:
        logger.info("Capture API request failed: %s", str(e))
        return None

# is_walmart_page
# 第三步：检测是否进入到 walmart 首页
# done

# 找到 Account 按钮，点击后，截图，1. 寻找 Account  2. 寻找 Walmart+

# ---------------------------------------------------------------------
## 1. 寻找 Account，点击 Account
# 1.1 进入  walmart.com/account, 寻找 Settings --> 点击 Settings: 
# ---------- # 1. 寻找 Address , ......
#-- 点击 Address, 截图分辨，寻点 "+ Add address"
#-- 表单识别并填写

# ---------- # 2. 寻找 Wallet , ......
##-- 点击 Wallet, 截图分辨， 寻点 "Credit/debit cart"
##-- 表单识别并填写

# ---------------------------------------------------------------------

## 2. 寻找 Walmart+， 点击 Walmart+
#
# ---------------------------------------------------------------------


### 如果你不知道要如何做 或 没有可以参考的指令，那么你发起钉钉通知

def process(account_info, action:str = "", idx = 0):
    start_time = time.time()  # Start timing

    if idx == 0:
        result = call_api(account_info, "start_browser")
        if result == 'connect client fail':
            logger.error('客户端未启动 ~ ~ ~')
            return
        logger.info(result)
    
    # Start from the specified action
    actions_sequence = [
        # "find_walmart",
        "click_account_btn",
        "enter_account",
        "click_account_setting",
        "click_address",
        "click_add_address"
    ]

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
        
        if current_action in ["click_account_setting"]:
            time.sleep(2.5)
        elif current_action in ["enter_account", "click_address", "click_add_address"]:
            time.sleep(1.5)
        elif current_action in ["click_account_btn"]:
            time.sleep(3.5)
        else:
            time.sleep(1)
        
        res = call_capture_api(action=current_action)
        if res is None:
            return {"status": "continue", "action": current_action}

    # 完成导航步骤后，进入表单填写
    if action in actions_sequence:
        action = "fill_address_form"
        
    if action == "fill_address_form":
        res = call_capture_api(action="fill_address_form", account_info=account_info)
        # 检查 res 是否为字典，并检查 'res' 键的值
        if (isinstance(res, dict) and res.get('res') != 1):
            return {"status": "fail", "action": "fill_address_form"}
        action = "fill_wallet_form"
    elif (isinstance(res, dict) and res.get('code') == 0):
        pass

    if action == "fill_wallet_form":
        # 如果添加地址成功，则进行创建银行卡
        res = call_capture_api(action="after_create_address_enter_wallet")
        if (isinstance(res, dict) and res.get('res') == 1):
            res = call_capture_api(action="fill_wallet_form", account_info=account_info)
            if isinstance(res, dict) and res.get('res') != 1:
                return {"status": "fail", "action": "fill_wallet_form"}
        elif (isinstance(res, dict) and res.get('code') == -100):
            logger.error(res.get('message'))
            
        action = "start_fress_30_day_trial"
    
    if action == "start_fress_30_day_trial":
        res = call_capture_api(action="start_fress_30_day_trial")
        if (isinstance(res, dict) and res.get('res') != 1):
            return {"status": "fail", "action": "start_fress_30_day_trial"}
        elif (isinstance(res, dict) and res.get('code') == 0):
            pass

    # 视觉模型确认是否开通会员成功
    res = call_capture_api(action="join_walmart_plus_result")
    is_join = 0
    if isinstance(res, dict):
        is_join = res.get('res')
        logger.info(f'join walmart+: {is_join}')
    
    # Calculate and log total execution time
    execution_time = time.time() - start_time
    logger.info(f"--------- Total execution time: {execution_time:.2f} seconds")

    # 最后 -- 关闭浏览器
    re = call_api(account_info, "close_browser")
    logger.info(f'close_browser: {re}')

    # 添加默认返回值，确保函数不会返回 None
    return {"status": "success", "action": ""}

def post_member_operate_res(account_info):
    url = "https://assist.weinpay.com/api/PyHandle/memberOperateRes"
    data_form = {
        "timestamp": 1722579064,  # 使用当前时间戳
        "signed": "8FD39EABE64DC7E6F56953FD8EE5B31C",  # 这里的签名需要根据您的逻辑生成
        "task_id": account_info["task_id"],
        "code": 0,
        "status": 0
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
    
    # Retry fetching the member operate list if it's empty
    while True:
        result = api_client.get_member_operate_list(page=1, limit=5, team=team)
        list = result['data']['list']
        
        if len(list) == 0:
            logger.info("List is empty, retrying in 15 seconds...")
            time.sleep(15)  # Wait for 15 seconds before retrying

        # logger.info(f'list == {list}')
        # account_info = result['data']['list'][0]
        for account_info in list:
            # walmart 帐户信息
            logger.info(account_info)
            
            res = {"status": "fail", "action": ""}
            for i in range(3):  # Retry up to 3 times
                next_action = res.get("action", "") if res is not None else ""
                res = process(account_info, next_action, i)
                if res is not None and res.get("status") not in ["fail", "continue"]:
                    break  # Exit the loop if successful or completed
                logger.info(f'res === {res}')
            else:
                logger.info("Failed after 3 attempts for account: %s", account_info)

            # Replace the original POST request code with a call to the new function
            result = post_member_operate_res(account_info)




        

