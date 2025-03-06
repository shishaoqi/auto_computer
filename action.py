# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from mouse_controller import MouseController  
from utils.logger import get_logger
import requests
import json
import time

logger = get_logger(__name__)

class Action:
    def __init__(self, screenshot_processor: ScreenshotProcessor, mouse_controller: MouseController) -> None:
        self.screenshot_processor = screenshot_processor
        self.mouse_controller = mouse_controller

    # 绑定收货地址
    def bind_address():
        pass

    # 创建银行卡或信用卡
    def create_bankCard():
        pass

    # 填写登录表单
    def login():
        pass

    def process_image_with_prompt(self, prompt: str, result: dict, expected_key: str):
        """
        处理图片并获取AI响应
        
        Args:
            prompt (str): 发送给AI的提示词
            result (dict): 包含原始和处理后图片路径的字典
            expected_key (str): 期望从AI响应中获取的键名
            
        Returns:
            Any: AI响应中指定键的值，如果处理失败则返回None
        """
        try:
            res = upload_images(result['original_image'], result['processed_image'], prompt)
            if not res:
                return None
            json_str = res['result']
            response_data = json.loads(json_str)
            return response_data.get(expected_key)
        except Exception as e:
            logger.error(f'处理图片失败: {str(e)}')
            return None

    def _click_element_by_number(self, number: int, parsed_content: list) -> bool:
        """
        根据序号点击元素的通用方法
        
        Args:
            number (int): 要点击元素的序号
            parsed_content (list): 解析后的内容列表
            
        Returns:
            bool: 点击是否成功
        """
        if number is None or not parsed_content:
            return False
            
        if 0 <= number < len(parsed_content):
            entry = parsed_content[number]
            logger.info(entry)
            if 'bbox' in entry:
                # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
                rel_x = (entry['bbox'][0] + entry['bbox'][2]) / 2
                rel_y = (entry['bbox'][1] + entry['bbox'][3]) / 2
                self.mouse_controller.click(rel_x, rel_y)
                return True
        return False
    
    def _click_element(self, bbox: list) -> bool:
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        rel_x = (bbox[0] + bbox[2]) / 2
        rel_y = (bbox[1] + bbox[3]) / 2
        self.mouse_controller.click(rel_x, rel_y)

    def _scroll_page_up(self, scroll_amount: int = 300):
        """
        向上滚动页面
        
        Args:
            scroll_amount (int): 滚动的像素量，正数表示向上滚动，默认300像素
        """
        self.mouse_controller.scroll(0, scroll_amount)

    def _scroll_page_down(self, scroll_amount: int = 300):
        """
        向下滚动页面
        
        Args:
            scroll_amount (int): 滚动的像素量，正数表示向下滚动，默认300像素
        """
        self.mouse_controller.scroll(0, -scroll_amount)  # 使用负值表示向下滚动

    def scroll_down_page(self, scroll_times: int = 1, scroll_amount: int = 300, delay: float = 0.5):
        """
        向下滚动页面指定次数
        
        Args:
            scroll_times (int): 滚动次数，默认为1次
            scroll_amount (int): 每次滚动的像素量，默认300像素
            delay (float): 每次滚动之间的延迟时间(秒)，默认0.5秒
        """
        for _ in range(scroll_times):
            self._scroll_page_down(scroll_amount)
            time.sleep(delay)

    def find_walmart(self):
        # 处理截图
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 请找出被标注的蓝色 Walmart 官网链接的序号。这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 注意：您的响应应遵循以下格式：{"walmart": 3}，3 是序号。请勿包含任何其他信息。'''
            
        #     walmart_number = self.process_image_with_prompt(prompt, result, "walmart")
            
        #     # 从 result['parsed_content'] 中遍历找出第 walmart_number 个的数据
        #     if self._click_element_by_number(walmart_number, result['parsed_content']):
        #         return result['parsed_content'][walmart_number]
            
        #     logger.warning(f'Walmart entry with number {walmart_number} not found')
        #     return None
            
        # else:
        #     logger.error('find_walmart error')
        bbox = [0.08867187798023224, 0.29027777910232544, 0.16875000298023224, 0.3125]
        self._click_element(bbox)

    def is_walmart_page(self):
        img = self.screenshot_processor.screenshot()
        image_paths = [img]
        prompt = '''请识别这张截图是不是 walmart 网站的首页。提示：walmart 网站首页是什么样的呢？首先，浏览器 URL 中能看到 walmart.com; 其次，页面顶栏最左边有 walmart logo，顶栏中间部分是搜索框。注意：您的响应应遵循以下格式：{"is_walmart_page": 1}。是 walmart 网站的首页，is_walmart_page 置为 1，不是置为 0。请勿包含任何其他信息。'''
        
        res = upload_multiple_images(image_paths, prompt)
        if not res:
            return None
        json_str = res['result']
        walmart_data = json.loads(json_str)
        return walmart_data.get("is_walmart_page")
    
    def click_account_btn(self):
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 请找出网页右上角的 Account 按钮。
        #                 注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
        #     number = self.process_image_with_prompt(prompt, result, "account")
        #     if self._click_element_by_number(number, result['parsed_content']):
        #         return result['parsed_content'][number]
        #     logger.warning(f'Walmart entry with number {number} not found')
        #     return None
        time.sleep(2.3)
        bbox = [0.9097564816474915, 0.08835277706384659, 0.9547790288925171, 0.13475187122821808]
        self._click_element(bbox)

        # 再次截图，--- 1. 寻找 Account  2. 寻找 Walmart+
    
    def enter_account(self):
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 请找出网页右上部的下拉框里的 Account。
        #                 注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
        #     number = self.process_image_with_prompt(prompt, result, "account")
        #     if self._click_element_by_number(number, result['parsed_content']):
        #         return result['parsed_content'][number]
        #     logger.warning(f'Walmart entry with number {number} not found')
        #     return None
        time.sleep(1.6)
        bbox = [0.9104751348495483, 0.20280081033706665, 0.9731246829032898, 0.2321944534778595]
        self._click_element(bbox)

    def click_account_setting(self):
        time.sleep(1.5)
        bbox = [0.2549503445625305, 0.8525451421737671, 0.3763135075569153, 0.8972681760787964]
        self._click_element(bbox)
        self.mouse_controller.scroll_down(400)

    def click_address(self):
        time.sleep(0.7)
        bbox = [0.2665168344974518, 0.745004415512085, 0.37486201524734497, 0.7754677534103394]
        self._click_element(bbox)

    def click_add_address(self):
        time.sleep(0.8)
        bbox = [0.38615599274635315, 0.28405794501304626, 0.42059326171875, 0.30172109603881836]
        self._click_element(bbox)
        time.sleep(0.35)
        self.mouse_controller.scroll_down(80)

    def click_wallet(self):
        time.sleep(0.7)
        bbox = [0.25694137811660767, 0.7728841304779053, 0.3740352988243103, 0.8032107949256897]
        self._click_element(bbox)

    

    def enter_walmart_plus(self):
        pass

def upload_images(original_image_path, processed_image_path, prompt, api_url="http://192.168.11.250:8004/analyze"):
    """
    上传原始图片和处理后的图片到服务器
    
    Args:
        original_image_path (str): 原始图片的路径
        processed_image_path (str): 处理后图片的路径
        prompt (str): 提示词
        api_url (str): API端点URL，默认为http://localhost:8004/analyze
        
    Returns:
        dict: 服务器返回的响应
    """
    # 获取文件扩展名
    original_ext = original_image_path.split('.')[-1]
    processed_ext = processed_image_path.split('.')[-1]
    
    # 准备文件
    files = [
        ('images', ('image1.' + original_ext, open(original_image_path, 'rb'), f'image/{original_ext}')),
        ('images', ('image2.' + processed_ext, open(processed_image_path, 'rb'), f'image/{processed_ext}'))
    ]
    
    # 准备数据
    data = {
        "prompt": prompt
    }
    
    try:
        # 发送请求
        response = requests.post(api_url, files=files, data=data)
        response.raise_for_status()  # 检查响应状态
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"上传失败: {str(e)}")
        return None
    finally:
        # 确保文件被正确关闭
        for _, (_, file_obj, _) in files:
            file_obj.close()

def upload_multiple_images(image_paths: list, prompt: str, api_url: str = "http://192.168.11.250:8004/analyze"):
    """
    上传多张图片到服务器
    
    Args:
        image_paths (list): 图片路径列表
        prompt (str): 提示词
        api_url (str): API端点URL，默认为http://192.168.11.250:8004/analyze
        
    Returns:
        dict: 服务器返回的响应
    """
    # 准备文件
    files = []
    try:
        for idx, image_path in enumerate(image_paths, 1):
            # 获取文件扩展名
            ext = image_path.split('.')[-1]
            # 添加文件到列表
            files.append(
                ('images', (f'image{idx}.{ext}', open(image_path, 'rb'), f'image/{ext}'))
            )
        
        # 准备数据
        data = {
            "prompt": prompt
        }
        
        # 发送请求
        response = requests.post(api_url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"上传失败: {str(e)}")
        return None
    
    finally:
        # 确保所有文件被正确关闭
        for _, (_, file_obj, _) in files:
            file_obj.close()