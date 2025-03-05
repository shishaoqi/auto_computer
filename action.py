# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from mouse_controller import MouseController  
from utils.logger import get_logger
import requests
import json 

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
            if 'bbox' in entry:
                # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
                rel_x = (entry['bbox'][0] + entry['bbox'][2]) / 2
                rel_y = (entry['bbox'][1] + entry['bbox'][3]) / 2
                self.mouse_controller.click(rel_x, rel_y)
                return True
        return False

    def find_walmart(self):
        # 处理截图
        success, result, status_code = self.screenshot_processor.process_screenshot()
        if status_code == 200:
            prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
                        请找出被标注的蓝色 Walmart 官网链接的序号。这些序号都被彩色方框包围，方框外就不是数字所属的部分。
                        注意：您的响应应遵循以下格式：{"walmart": 3}，3 是序号。请勿包含任何其他信息。'''
            
            walmart_number = self.process_image_with_prompt(prompt, result, "walmart")
            
            # 从 result['parsed_content'] 中遍历找出第 walmart_number 个的数据
            if self._click_element_by_number(walmart_number, result['parsed_content']):
                return result['parsed_content'][walmart_number]
            
            logger.warning(f'Walmart entry with number {walmart_number} not found')
            return None
            
        else:
            logger.error('find_walmart error')

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
        success, result, status_code = self.screenshot_processor.process_screenshot()
        if status_code == 200:
            prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
                        第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
                        请找出网页右上角的 Account 按钮。
                        注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
            number = self.process_image_with_prompt(prompt, result, "account")
            if self._click_element_by_number(number, result['parsed_content']):
                return result['parsed_content'][number]
            logger.warning(f'Walmart entry with number {number} not found')
            return None

        # 再次截图，--- 1. 寻找 Account  2. 寻找 Walmart+
    
    def enter_account(self):
        success, result, status_code = self.screenshot_processor.process_screenshot()
        if status_code == 200:
            prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
                        第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
                        请找出网页右上部的下拉框里的 Account。
                        注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
            number = self.process_image_with_prompt(prompt, result, "account")
            if self._click_element_by_number(number, result['parsed_content']):
                return result['parsed_content'][number]
            logger.warning(f'Walmart entry with number {number} not found')
            return None


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