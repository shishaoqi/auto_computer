# 所有步骤集中地
import requests
from dotenv import load_dotenv
import os
import time
from utils.logger import get_logger

# Load environment variables from .env file
load_dotenv()
logger = get_logger(__name__)

# 第一步：打开浏览器（已进入到搜索 walmart 结果的页）
def call_start_api():
    url = os.getenv('START_API_URL', 'http://localhost:5000') + '/start'  # Default fallback if not set in .env
    
    try:
        response = requests.post(url)
        
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
        return None

# find_walmart
# 第二步：截图分辨, 找到 walmart, 打开它
### 异常：找不到，取截图，询问当前是什么情况，有什么处理办法。(例如有弹窗，关闭弹窗)
def call_capture_api(action=""):
    """
    Call the capture API with specified action
    """
    url = os.getenv('CAPTURE_API_URL', 'http://localhost:5000') + '/capture'  # Default fallback if not set in .env
    
    # Add action as query parameter instead of JSON payload
    params = {
        "action": action
    }
    
    try:
        response = requests.get(url, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info("Capture API Success for action '%s': %s", action, result)
            return result
        else:
            logger.info("Error: %d", response.status_code)
            logger.info("Error message: %s", response.json())
            return None
            
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

if __name__ == '__main__':
    start_time = time.time()  # Start timing
    
    logger.info('auto_server')
    result = call_start_api()
    logger.info(result)

    time.sleep(0.5)
    res = call_capture_api(action="find_walmart")

    time.sleep(1.5)
    re = call_capture_api(action="is_walmart_page")
    
    # Calculate and log total execution time
    execution_time = time.time() - start_time
    logger.info(f"Total execution time: {execution_time:.2f} seconds")
    
    if re['res'] == 1:
        time.sleep(3)
        res = call_capture_api(action="click_account_btn")

        res = call_capture_api(action='enter_account')
        res = call_capture_api(action="click_account_setting")
        res = call_capture_api(action="click_address") # 进入新增 address 页
        res = call_capture_api(action="click_add_address")
        