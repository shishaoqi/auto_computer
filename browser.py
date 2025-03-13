from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from utils.logger import get_logger
import requests
from option_status import OPTION_STATUS
import os
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = get_logger(__name__)

# 定义常量
ADS_REQUEST_TIMEOUT = (
    int(os.getenv('ADS_REQUEST_TIMEOUT_CONNECT', '5')), 
    int(os.getenv('ADS_REQUEST_TIMEOUT_READ', '25'))
)
MAX_ERROR_RETRIES = int(os.getenv('MAX_ERROR_RETRIES', '5'))
DEFAULT_OPERATION_INTERVAL = float(os.getenv('DEFAULT_OPERATION_INTERVAL', '1'))
DEFAULT_ADS_HOST = os.getenv('DEFAULT_ADS_HOST', 'local.adspower.net:50325')

class WalmartAccount(BaseModel):
    """Walmart account credentials model"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Account password")
    account_password: str = Field(..., description="Phone number or secondary password")

class Browser:
    def __init__(self) -> None:
        self.ads_host: str = DEFAULT_ADS_HOST
        self.ads_id: str = ''
        self.ads_key_id: str = ''
        self.account_info: Optional[WalmartAccount] = None
        self.last_error_status: int = 0
        self._is_browser_running: bool = False

    def init_user_info(self, data):
        self.ads_id = data['ads_id']
        self.ads_key_id = data['ads_id']  # 设置 ads_key_id

        self.account_info = WalmartAccount(
            email=data['email'],
            password=data['password'],
            account_password=data['account_password']
        )

    def start_browser(self):
        ads_api_start_url = f"http://{self.ads_host}/api/v1/browser/start"
        logger.info(f"Starting browser with URL: {ads_api_start_url}")
        
        params = {
            "user_id": self.ads_key_id,
            "open_tabs": 1,
        }
        max_retries = 3
        for attempt in range(max_retries):
            resp = self.ads_get(ads_api_start_url, params=params)
            
            if not resp:
                logger.warning(f"No response on attempt {attempt+1}/{max_retries}, retrying...")
                time.sleep(2)
                continue
            
            resp_json = resp.json()
            logger.info(resp_json)
            
            if resp_json["code"] == 0:
                # 成功获取响应
                resp_data = resp_json["data"]
                logger.info(resp_data)
                break
            elif resp_json["code"] != 0:
                if resp_json["msg"] == "user account does not exist":
                    self.last_error_status = OPTION_STATUS.STATUS_ADS_ID_NOT_EXSIT_ERROR
                    logger.error(f'Browser start failed: ADS ID does not exist: {self.ads_key_id}')
                    return None
                elif "User_id is already open" in resp_json["msg"]:
                    # 先尝试关闭已存在的实例
                    logger.warning(f"Browser instance already open for {self.ads_key_id}, attempting to close it first")
                    self.close_browser(self.ads_key_id)
                    time.sleep(2)
                    continue
                else:
                    logger.error(f'Browser start failed: {resp_json["msg"]}')
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying ({attempt+1}/{max_retries})...")
                        time.sleep(2)
                        continue
                    return None
            
        self._is_browser_running = True

    def close_browser(self, ads_key_id=None):
        """
        关闭浏览器实例
        
        Args:
            ads_key_id: 可选的ADS ID，如果未提供则使用当前实例的ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            # 如果未提供ads_key_id，使用当前实例的ID
            ads_key_id = ads_key_id or self.ads_key_id
            
            if not ads_key_id:
                logger.warning("No ADS key ID provided for browser closing")
                return False
            
            params = {"user_id": ads_key_id}
            open_url = f"http://{self.ads_host}/api/v1/browser/stop"
            
            resp = self.ads_get(open_url, params=params, timeout=(5, 15))
            if not resp:
                logger.error(f"Failed to get response when closing browser for user_id={ads_key_id}")
                return False
            
            resp_json = resp.json()
            logger.info(f'close_browser response: {resp_json}')
            if resp_json["code"] != 0:
                if "User_id is not open" == resp_json["msg"] or 'user account does not exist' == resp_json["msg"]:
                    return True
                else:
                    logger.error(f'ads_close user_id={ads_key_id} error={resp_json["msg"]}')
                    return False
            else:
                # 清理资源
                if ads_key_id == self.ads_key_id:
                    self.driver = None
                    self._is_browser_running = False
                return True
            
        except Exception as e:
            logger.error(f"Exception in close_browser for user_id={ads_key_id}: {str(e)}")
            
        return False

    def ads_get(self, url: str, **kwargs) -> Optional[requests.Response]:
        try:
            kwargs.pop('ads_wait', None)
            kwargs['timeout'] = ADS_REQUEST_TIMEOUT
            resp = requests.get(url, **kwargs)
            time.sleep(DEFAULT_OPERATION_INTERVAL)
            return resp
            
        except requests.RequestException as e:
            logger.error(f"ads_get failed: url={url}, error={str(e)}")
            return None