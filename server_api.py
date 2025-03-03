from flask import Flask, jsonify
from PIL import ImageGrab
import os
from datetime import datetime

app = Flask(__name__)

# 确保screenshots文件夹存在
if not os.path.exists('screenshots'):
    os.makedirs('screenshots')

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
