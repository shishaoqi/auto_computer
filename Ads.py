from pydantic import BaseModel, Field
from typing import Optional
from utils.logger import get_logger
import threading
import requests
from option_status import OPTION_STATUS
import undetected_chromedriver as uc
from utils import func
import os
import shutil
import time
import re
from selenium.webdriver.chrome.webdriver import WebDriver

logger = get_logger(__name__)

# 定义常量
ADS_REQUEST_TIMEOUT = (5, 25)
MAX_ERROR_RETRIES = 5
DEFAULT_OPERATION_INTERVAL = 1

class WalmartAccount(BaseModel):
    """Walmart account credentials model"""
    email: str = Field(..., description="User email")
    password: str = Field(..., description="Account password")
    account_password: str = Field(..., description="Phone number or secondary password")

# 全局变量初始化
g_ads_op_lock = threading.RLock()
g_ads_op_interval = DEFAULT_OPERATION_INTERVAL
g_ads_error_cnt = 0

def ads_get(url: str, **kwargs) -> Optional[requests.Response]:
    """
    执行 ADS GET 请求，包含重试和错误处理机制
    
    Args:
        url: 请求URL
        **kwargs: 请求参数
        
    Returns:
        Response object or None if request fails
    """
    with g_ads_op_lock:
        global g_ads_error_cnt
        try:
            kwargs.pop('ads_wait', None)
            kwargs['timeout'] = ADS_REQUEST_TIMEOUT
            resp = requests.get(url, **kwargs)
            g_ads_error_cnt = 0
            
            # API 特殊处理
            if '/api/v1/user/list' in url:
                time.sleep(1)
            else:
                time.sleep(g_ads_op_interval)
            return resp
            
        except requests.RequestException as e:
            str_msg = str(e)
            if ('Failed to establish a new connection: [WinError 10061]' in str_msg or 
                'Read timed out.' in str_msg):
                g_ads_error_cnt += 1
                if g_ads_error_cnt >= MAX_ERROR_RETRIES:
                    g_ads_error_cnt = 0
                    # TODO: Implement ads_restart()
                    
            logger.error(f"ads_get failed: url={url}, error={str_msg}")
            return None

def ads_post(url: str, **kwargs) -> Optional[requests.Response]:
    """
    执行 ADS POST 请求，包含重试和错误处理机制
    
    Args:
        url: 请求URL
        **kwargs: 请求参数
        
    Returns:
        Response object or None if request fails
    """
    with g_ads_op_lock:
        global g_ads_error_cnt
        try:
            kwargs.pop('ads_wait', None)
            kwargs['timeout'] = ADS_REQUEST_TIMEOUT
            resp = requests.post(url, **kwargs)
            g_ads_error_cnt = 0
            time.sleep(g_ads_op_interval)
            return resp
            
        except requests.RequestException as e:
            str_msg = str(e)
            if ('Failed to establish a new connection: [WinError 10061]' in str_msg or 
                'Read timed out.' in str_msg):
                g_ads_error_cnt += 1
                if g_ads_error_cnt >= MAX_ERROR_RETRIES:
                    g_ads_error_cnt = 0
                    # TODO: Implement ads_restart()
                    
            logger.error(f"ads_post failed: url={url}, error={str_msg}")
            return None

class Ads:
    """ADS browser automation controller class"""
    
    def __init__(self) -> None:
        self.ads_host: str = ''
        self.ads_id: str = ''
        self.ads_key_id: str = ''  # 添加缺失的属性
        self.account_info: WalmartAccount = None
        self.driver: Optional[WebDriver] = None
        self.cache_driver_file: str = ''
        self.last_error_status: int = 0

    def start_browser(self, data: dict) -> None:
        """
        Initialize browser with account data
        
        Args:
            data: Dictionary containing ads_id and account credentials
        """
        try:
            self.ads_id = data['ads_id']
            self.ads_key_id = data['ads_id']  # 设置 ads_key_id
            self.ads_host = "local.adspower.net:50325"  # 设置默认的 ads_host
            self.account_info = WalmartAccount(
                email=data['email'],
                password=data['password'],
                account_password=data['account_password']
            )
            
            # 调用 _api_start_browser 来实际启动浏览器
            self.driver = self._api_start_browser()
            if not self.driver:
                raise Exception("Failed to start browser")
            
        except Exception as e:
            logger.error(f'start_browser initialization failed: {str(e)}')
            raise

    def _api_start_browser(self) -> Optional[WebDriver]:
        """
        Start the ADS browser instance
        
        Returns:
            WebDriver instance or None if startup fails
        """
        params = {
            "user_id": self.ads_key_id,
            # "headless": 1,  # 无头模式配置
        }
        
        ads_api_start_url = f"http://{self.ads_host}/api/v1/browser/start"
        logger.info(f"Starting browser with URL: {ads_api_start_url}")
        resp = ads_get(ads_api_start_url, params=params)
        
        if not resp or resp.json()["code"] != 0:
            if resp and resp.json()["msg"] == "user account does not exist":
                self.last_error_status = OPTION_STATUS.STATUS_ADS_ID_NOT_EXSIT_ERROR
            logger.error(f'Browser start failed for ads_key_id={self.ads_key_id}: {resp.json()["msg"] if resp else "No response"}')
            return None

        resp_data = resp.json()["data"]
        driver_path = resp_data["webdriver"]
        selenium_debugger_address = resp_data["ws"]["selenium"]
        
        return self._setup_chrome_driver(driver_path, selenium_debugger_address)

    def _setup_chrome_driver(self, driver_path: str, debugger_address: str) -> WebDriver:
        """
        Setup and configure Chrome WebDriver
        
        Args:
            driver_path: Path to the Chrome driver
            debugger_address: Selenium debugger address
            
        Returns:
            Configured WebDriver instance
        """
        chrome_exe = os.path.join(os.path.dirname(driver_path), 'SunBrowser.exe')
        
        # 设置Chrome选项
        options = uc.ChromeOptions()
        options.debugger_address = debugger_address
        
        # 准备driver文件
        chrome_version = re.findall("chrome_([\d]{1,3})", driver_path)[0]
        formatted_time = time.strftime("%Y%m%d", time.localtime())
        day_driver_dir = os.path.join(func.get_driver_dir(), formatted_time)
        os.makedirs(day_driver_dir, exist_ok=True)
        
        chromedriver_name = f'chromedriver_{self.ads_key_id}_{chrome_version}.exe'
        dest_driver_file = os.path.join(day_driver_dir, chromedriver_name)
        
        # 确保进程未运行并复制driver
        func.kill_process_by_name(chromedriver_name)
        if not os.path.exists(dest_driver_file):
            shutil.copy(driver_path, dest_driver_file)
            try:
                os.chmod(dest_driver_file, 0o777)
            except OSError as e:
                logger.warning(f"Failed to set driver permissions: {e}")
        
        self.cache_driver_file = dest_driver_file
        self.driver = uc.Chrome(
            options=options,
            browser_executable_path=chrome_exe,
            driver_executable_path=dest_driver_file
        )
        
        return self.driver