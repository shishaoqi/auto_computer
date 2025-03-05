# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from utils.logger import get_logger

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
            print(result['parsed_content'])
            pass
        else:
            logger.error('find_walmart error')