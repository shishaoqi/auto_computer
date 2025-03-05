# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from utils.logger import get_logger
import requests

logger = get_logger(__name__)

class Action:
    def __init__(self, screenshot_processor: ScreenshotProcessor) -> None:
        self.screenshot_processor = screenshot_processor

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
请找出标注了 "Walmart Official Site" 的序号。这些序号都被彩色方框包围，方框外就不是数字所属的部分。
请按以下JSON格式返回结果：{"Walmart Official Site": 序号}
注意：仅返回JSON格式数据，无需其他说明。'''
            res = upload_images(result['original_image'], result['processed_image'], prompt)
            print(res)
            pass
        else:
            logger.error('find_walmart error')

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