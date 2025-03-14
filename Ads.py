from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
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
                    logger.warning(f"Maximum error retries reached ({MAX_ERROR_RETRIES}), should restart ADS")
                    
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

def ads_restart():
    """
    重启 ADS 服务
    当连续错误次数达到阈值时调用
    """
    logger.info("Attempting to restart ADS service")
    try:
        # 关闭所有浏览器实例
        close_url = f"http://local.adspower.net:50325/api/v1/browser/stop-all"
        resp = requests.get(close_url, timeout=ADS_REQUEST_TIMEOUT)
        
        if resp.status_code == 200 and resp.json().get("code") == 0:
            logger.info("Successfully stopped all ADS browser instances")
            time.sleep(2)  # 给系统一些时间来释放资源
            return True
        else:
            logger.error(f"Failed to stop ADS browsers: {resp.text if resp else 'No response'}")
            return False
    except Exception as e:
        logger.error(f"Error during ADS restart: {str(e)}")
        return False

class Ads:
    """ADS browser automation controller class"""
    
    def __init__(self) -> None:
        self.ads_host: str = DEFAULT_ADS_HOST
        self.ads_id: str = ''
        self.ads_key_id: str = ''
        self.account_info: Optional[WalmartAccount] = None
        self.driver: Optional[Any] = None
        self.cache_driver_file: str = ''
        self.last_error_status: int = 0
        self._is_browser_running: bool = False

    @property
    def is_browser_running(self) -> bool:
        """检查浏览器是否正在运行"""
        return self._is_browser_running and self.driver is not None

    def start_browser(self, data: dict) -> None:
        """
        Initialize browser with account data
        
        Args:
            data: Dictionary containing ads_id and account credentials
        """
        try:
            self.ads_id = data['ads_id']
            self.ads_key_id = data['ads_id']  # 设置 ads_key_id
            self.ads_host = DEFAULT_ADS_HOST
            self.account_info = WalmartAccount(
                email=data['email'],
                password=data['password'],
                account_password=data['account_password']
            )
            
            # 调用 _api_start_browser 来实际启动浏览器
            self.driver = self._api_start_browser()
            # if not self.driver:
            #     raise Exception("Failed to start browser")
            
        except Exception as e:
            logger.error(f'start_browser initialization failed: {str(e)}')
            raise

    def _api_start_browser(self) -> Optional[Any]:
        """
        Start the ADS browser instance
        
        Returns:
            WebDriver instance or None if startup fails
        """
        params = {
            "user_id": self.ads_key_id,
            # "headless": 1,  # 无头模式配置
            "open_tabs": 1,
        }
        
        ads_api_start_url = f"http://{self.ads_host}/api/v1/browser/start"
        logger.info(f"Starting browser with URL: {ads_api_start_url}")
        
        # 添加重试逻辑
        max_retries = 3
        for attempt in range(max_retries):
            resp = ads_get(ads_api_start_url, params=params)
            
            if not resp:
                logger.warning(f"No response on attempt {attempt+1}/{max_retries}, retrying...")
                time.sleep(2)
                continue
            
            resp_json = resp.json()
            if resp_json["code"] != 0:
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
            
            # 成功获取响应
            resp_data = resp_json["data"]
            # driver_path = resp_data["webdriver"]
            # selenium_debugger_address = resp_data["ws"]["selenium"]
            
            # driver = self._setup_chrome_driver(driver_path, selenium_debugger_address)
            # if driver:
            #     self._is_browser_running = True
            #     return driver
            logger.info(resp_data)
        return None

    def _setup_chrome_driver(self, driver_path: str, debugger_address: str) -> Any:
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
        # chrome_version = re.findall("chrome_([\d]{1,3})", driver_path)[0]
        # formatted_time = time.strftime("%Y%m%d", time.localtime())
        # day_driver_dir = os.path.join(func.get_driver_dir(), formatted_time)
        # os.makedirs(day_driver_dir, exist_ok=True)
        
        # chromedriver_name = f'chromedriver_{self.ads_key_id}_{chrome_version}.exe'
        # dest_driver_file = os.path.join(day_driver_dir, chromedriver_name)
        
        # # 确保进程未运行并复制 driver
        # func.kill_process_by_name(chromedriver_name)
        # if not os.path.exists(dest_driver_file):
        #     shutil.copy(driver_path, dest_driver_file)
        #     try:
        #         os.chmod(dest_driver_file, 0o777)
        #     except OSError as e:
        #         logger.warning(f"Failed to set driver permissions: {e}")
        
        # self.cache_driver_file = dest_driver_file
        self.driver = uc.Chrome(
            options=options,
            browser_executable_path=chrome_exe,
            driver_executable_path=driver_path # dest_driver_file
        )
        
        try:
            # 先最小化窗口
            # logger.info("Minimizing browser window")
            self.driver.minimize_window()
            time.sleep(0.5)  # 短暂等待以确保最小化完成
            
            # 然后最大化窗口
            # logger.info("Maximizing browser window")
            self.driver.maximize_window()
        except Exception as e:
            logger.warning(f"Failed to minimize/maximize browser window: {e}")
        
        return self.driver
    
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
            
            resp = ads_get(open_url, params=params, timeout=(5, 15))
            if not resp:
                logger.error(f"Failed to get response when closing browser for user_id={ads_key_id}")
                return False
            
            resp_json = resp.json()
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

    def __del__(self):
        """析构函数，确保资源被正确释放"""
        try:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
                
            if self.ads_key_id:
                try:
                    self.close_browser(self.ads_key_id)
                except:
                    pass
        except:
            pass

    def check_ads_status(self) -> Dict[str, Any]:
        """
        检查ADS服务状态
        
        Returns:
            Dict: 包含状态信息的字典
        """
        try:
            status_url = f"http://{self.ads_host}/api/v1/status"
            resp = ads_get(status_url, timeout=(3, 5))
            
            if resp and resp.status_code == 200:
                return {
                    "status": "online",
                    "details": resp.json()
                }
            return {
                "status": "offline",
                "details": None
            }
        except Exception as e:
            logger.error(f"Error checking ADS status: {str(e)}")
            return {
                "status": "error",
                "details": str(e)
            }