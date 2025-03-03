from flask import Flask, jsonify
from PIL import ImageGrab
import os
from datetime import datetime
from Ads import Ads  # 添加Ads导入

app = Flask(__name__)

# 初始化Ads实例
ads = Ads()

# 确保screenshots文件夹存在
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

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
            
        ads.driver.execute("newWindow", {'url': 'https://www.google.com/search?p=walmart'})
        
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
        filename = f'screenshots/screenshot_{timestamp}.png'
        
        # 捕获整个屏幕
        screenshot = ImageGrab.grab()
        
        # 保存截图
        screenshot.save(filename)
        
        return jsonify({
            'status': 'success',
            'message': '截图已保存',
            'filename': filename
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'截图失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
