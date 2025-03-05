import base64
import io
from datetime import datetime
from PIL import ImageGrab, Image
import requests
import os

class ScreenshotProcessor:
    def __init__(self):
        # 确保screenshots和detecting文件夹存在
        for folder in ['screenshots', 'detecting']:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def process_screenshot(self):
        """
        捕获屏幕截图并进行处理，返回处理结果
        Returns:
            tuple: (success_bool, result_dict, status_code)
        """
        # 获取当前时间戳作为文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_filename = f'screenshots/screenshot_{timestamp}.png'
        detecting_filename = f'detecting/detected_{timestamp}.png'
        
        try:
            # 捕获整个屏幕
            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_filename)
            
            # 上传图片到处理服务器
            with open(screenshot_filename, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(
                    'http://192.168.11.250:8003/process_image',
                    files=files,
                    stream=True,
                    timeout=(30, 300)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result['status'] == 'success':
                        # 处理图片
                        image_data = base64.b64decode(result['image'])
                        image = Image.open(io.BytesIO(image_data))
                        image.save(detecting_filename)
                        
                        return True, {
                            'status': 'success',
                            'message': '截图已保存并处理',
                            'original_image': screenshot_filename,
                            'processed_image': detecting_filename,
                            'parsed_content': result['parsed_content']
                        }, 200
                        
                error_detail = ''
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text if response.text else '无法获取详细错误信息'
                    
                return False, {
                    'status': 'error',
                    'message': f'图片处理失败: HTTP {response.status_code}',
                    'detail': error_detail
                }, 500
                    
        except requests.exceptions.Timeout:
            return False, {
                'status': 'error',
                'message': '图片处理超时，请稍后重试'
            }, 504
        except Exception as e:
            return False, {
                'status': 'error',
                'message': f'截图或处理失败: {str(e)}'
            }, 500 