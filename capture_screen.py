import pyautogui
import time
import os

class LocalDesktopAgent:
    """
    使用本地桌面进行屏幕截图和鼠标操作。
    原来的 OmniTool 中可能在 vm_agent.py 里调用虚拟机 API，
    这里直接使用 pyautogui 处理本地操作。
    """

    def __init__(self):
        # 设置基础目录为脚本所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.screenshot_dir = os.path.join(self.base_dir, 'screenshots')
        
        # 确保screenshots目录存在
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def capture_screen(self, region=None):
        """
        截取本地桌面截图。可选参数 region 以 (left, top, width, height) 指定区域。
        如果 region 为 None 则截取整个屏幕。
        """
        screenshot = pyautogui.screenshot(region=region)
        return screenshot

    def save_screenshot(self, screenshot, filename):
        """
        保存截图到文件。
        自动创建必要的目录结构。
        """
        try:
            # 确保filename是绝对路径
            if not os.path.isabs(filename):
                filename = os.path.join(self.screenshot_dir, filename)
                
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            screenshot.save(filename, 'PNG')
            return True
        except Exception as e:
            print(f"保存截图时出错: {e}")
            return False

    def click_at(self, x, y, clicks=1, interval=0.25, button='left'):
        """
        在指定坐标 (x, y) 上执行点击操作。
        - clicks: 点击次数
        - interval: 单次点击间隔
        - button: 可选 'left' 或 'right'
        """
        # 移动鼠标到目标位置
        pyautogui.moveTo(x, y)
        time.sleep(0.1)  # 确保鼠标移动完成
        pyautogui.click(clicks=clicks, interval=interval, button=button)

    def perform_action(self, action):
        """
        执行从 UI 元素解析任务中获得的操作指令。
        action 示例：
            {
              "type": "click",
              "x": 100,
              "y": 200,
              "clicks": 1
            }
        """
        if action.get('type') == 'click':
            self.click_at(action.get('x', 0), action.get('y', 0), action.get('clicks', 1))
        # 后续可根据需要添加更多类型的操作，例如键盘输入、滚动等

if __name__ == '__main__':
    agent = LocalDesktopAgent()
    
    # 示例：截取整个屏幕并保存为文件
    screenshot = agent.capture_screen()
    filename = 'local_screenshot.png'  # 现在可以直接使用文件名，save_screenshot会处理路径
    if agent.save_screenshot(screenshot, filename):
        print(f"截图已保存到: {os.path.join(agent.screenshot_dir, filename)}")
    else:
        print("保存截图失败")

    
    
    # 示例：在屏幕 (x=100, y=200) 位置执行单次左键点击
    agent.click_at(100, 200)
    print("在（100,200）位置执行了点击操作")
