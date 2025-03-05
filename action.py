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

    # 查找 walmart
    def find_walmart(self):
        # 处理截图
        success, result, status_code = self.screenshot_processor.process_screenshot()
        if status_code == 200:
            # 询问 qwen2.5-vl 哪个是 walmart, 获取 id ，取出
            # print(result['parsed_content'])
            prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
                        请找出被标注的蓝色 Walmart 官网链接的序号。这些序号都被彩色方框包围，方框外就不是数字所属的部分。
                        注意：您的响应应遵循以下格式：{"walmart": 3}，3 是序号。请勿包含任何其他信息。'''
            res = upload_images(result['original_image'], result['processed_image'], prompt)
            # 使用两张图片（原来的用法）
            # res = upload_multiple_images(
            #     [result['original_image'], result['processed_image']],
            #     prompt
            # )
            print(res)
            json_str = res['result']
            walmart_data = json.loads(json_str)
            walmart_number = walmart_data.get("walmart")
            # 从 result['parsed_content'] 中遍历找出第 walmart_number 个的数据
            # 通过索引位置找到对应的数据
            if walmart_number and result['parsed_content']:
                # walmart_number 从1开始，需要减1来匹配0基数的列表索引
                if 0 <= walmart_number < len(result['parsed_content']):
                    walmart_entry = result['parsed_content'][walmart_number]
                    # 获取点击坐标并执行点击
                    if 'bbox' in walmart_entry:
                        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
                        rel_x = (walmart_entry['bbox'][0] + walmart_entry['bbox'][2]) / 2
                        rel_y = (walmart_entry['bbox'][1] + walmart_entry['bbox'][3]) / 2
                        self.mouse_controller.click(rel_x, rel_y)
                    return walmart_entry
            
            logger.warning(f'Walmart entry with number {walmart_number} not found')
            return None
            
        else:
            logger.error('find_walmart error')

    def is_walmart_page(self):
        # 使用多张图片
        img = self.screenshot_processor.screenshot()
        image_paths = [img]
        prompt = '''请识别这张截图是不是 walmart 网站的首页。提示：walmart 网站首页是什么样的呢？首先，浏览器 URL 中能看到 walmart.com; 其次，页面顶栏最左边有 walmart logo，顶栏中间部分是搜索框。注意：您的响应应遵循以下格式：{"is_walmart_page": 1}。是 walmart 网站的首页，is_walmart_page 置为 1，不是置为 0。请勿包含任何其他信息。'''
        res = upload_multiple_images(image_paths, prompt)
        json_str = res['result']
        walmart_data = json.loads(json_str)
        is_walmart_page = walmart_data.get("is_walmart_page")
        return is_walmart_page

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