import base64
import io
from flask import Flask, jsonify
from PIL import ImageGrab
from PIL import Image
import os
import time
import requests
from datetime import datetime
from Ads import Ads  # 添加Ads导入

app = Flask(__name__)

# 初始化Ads实例
ads = Ads()

# 确保screenshots和detecting文件夹存在
for folder in ['screenshots', 'detecting']:
    if not os.path.exists(folder):
        os.makedirs(folder)

@app.route('/start', methods=['POST'])
def start_browser():
    try:
        # 示例数据，实际使用时应该从请求中获取
        test_data = {
            'ads_id': 'kl3ssaa', # 'kp25jst'
            'email': 'test@example.com',
            'password': 'test_password',
            'account_password': 'test_account_password'
        }
        
        ads.start_browser(test_data)
        if not ads.driver:
            return jsonify({
                'status': 'error',
                'message': '浏览器启动失败: driver is None'
            }), 500
            
        YAHOO_WALMART_SEARCH = 'https://www.google.com/search?q=walmart'
        #ads.driver.execute("newWindow", {'url': 'https://www.google.com/search?p=walmart'})
        # 记录当前窗口句柄
        original_handles = ads.driver.window_handles
        
        # 打开新窗口
        ads.driver.execute("newWindow", {'url': YAHOO_WALMART_SEARCH})
        
        # 等待新窗口出现并获取新窗口句柄
        timeout = 10
        new_handle = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_handles = ads.driver.window_handles
            if len(current_handles) > len(original_handles):
                new_handle = [h for h in current_handles if h not in original_handles][0]
                break
            time.sleep(0.5)
            
        if not new_handle:
            raise Exception("新窗口未能成功打开")
            
        # 切换到新窗口
        ads.driver.switch_to.window(new_handle)
        
        # 确保页面加载完成
        ads.driver.get(YAHOO_WALMART_SEARCH)
        
        return jsonify({
            'status': 'success',
            'message': '浏览器启动成功'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'浏览器启动失败: {str(e)}'
        }), 500

@app.route('/capture', methods=['GET'])
def capture_screen():
    try:
        # 获取当前时间戳作为文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_filename = f'screenshots/screenshot_{timestamp}.png'
        detecting_filename = f'detecting/detected_{timestamp}.png'
        
        try:
            # 捕获整个屏幕
            screenshot = ImageGrab.grab()
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'截图失败: {str(e)}'
            }), 500
        
        try:
            # 保存截图
            screenshot.save(screenshot_filename)
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'保存截图失败: {str(e)}'
            }), 500

        # 上传图片到处理服务器
        try:
            with open(screenshot_filename, 'rb') as image_file:
                files = {'file': image_file}
                response = requests.post(
                    'http://192.168.11.250:8003/process_image',
                    files=files,
                    stream=True,
                    timeout=(30, 300)  # (连接超时, 读取超时) 单位：秒
                )
                
                if response.status_code == 200:
                    result = response.json()
            
                    if result['status'] == 'success':
                        # 处理图片
                        image_data = base64.b64decode(result['image'])
                        image = Image.open(io.BytesIO(image_data))
                        
                        # 保存处理后的图片
                        image.save(detecting_filename)
                        print(f"处理后的图片已保存到：{detecting_filename}")
                        
                        # 打印解析内容
                        print("\n解析内容：")
                        for item in result['parsed_content']:
                            print(item)
                            

                        # 保存处理后的图片
                        # with open(detecting_filename, 'wb') as f:
                        #     for chunk in response.iter_content(chunk_size=8192):
                        #         if chunk:
                        #             f.write(chunk)
                        
                        # 

                        return jsonify({
                            'status': 'success',
                            'message': '截图已保存并处理',
                            'original_image': screenshot_filename,
                            'processed_image': detecting_filename
                        }), 200
                    else:
                        print(f"请求失败，状态码：{response.status_code}")
                        return False
                else:
                    error_detail = ''
                    try:
                        error_detail = response.json()
                    except:
                        try:
                            error_detail = response.text
                        except:
                            error_detail = '无法获取详细错误信息'
                            
                    return jsonify({
                        'status': 'error',
                        'message': f'图片处理失败: HTTP {response.status_code}',
                        'detail': error_detail
                    }), 500

        except requests.exceptions.Timeout:
            return jsonify({
                'status': 'error',
                'message': '图片处理超时，请稍后重试'
            }), 504  # Gateway Timeout
        except requests.exceptions.RequestException as e:
            return jsonify({
                'status': 'error',
                'message': f'上传图片失败: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'截图或处理失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
