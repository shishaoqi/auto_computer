from PIL import Image
import pyautogui
import time
import logging

class MouseController:
    def __init__(self):
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # 每个操作之间的延迟
        self.logger = logging.getLogger(__name__)

    def click(self, rel_x, rel_y):
        """
        执行点击操作，将相对坐标转换为实际屏幕坐标
        :param rel_x: x轴相对坐标(0-1范围)
        :param rel_y: y轴相对坐标(0-1范围)
        """
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 将相对坐标转换为实际屏幕坐标
            actual_x = int(rel_x * screen_width)
            actual_y = int(rel_y * screen_height)
            
            # 执行点击
            self._click_element(actual_x, actual_y)
            
            return True
        except Exception as e:
            self.logger.error(f"点击操作失败: {str(e)}")
            return False

    def process_clicks(self, image_path, parsed_content):
        """
        处理点击事件
        :param image_path: 处理后的图片路径
        :param parsed_content: 解析出的内容列表，每项包含坐标和类型信息
        :return: bool 是否成功执行所有点击
        """
        try:
            # 加载图片获取尺寸
            with Image.open(image_path) as img:
                img_width, img_height = img.size

            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()

            for item in parsed_content:
                try:
                    # 确保item包含必要的信息
                    if not all(key in item for key in ['box', 'type']):
                        self.logger.warning(f"跳过不完整的项: {item}")
                        continue

                    # 获取中心点坐标
                    x1, y1, x2, y2 = item['box']
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2

                    # 根据不同类型执行不同的点击操作
                    if item['type'] == 'button':
                        self._click_element(center_x, center_y)
                    elif item['type'] == 'input':
                        self._click_element(center_x, center_y, double_click=True)
                    elif item['type'] == 'link':
                        self._click_element(center_x, center_y)
                    
                    # 操作后短暂等待
                    time.sleep(0.5)

                except Exception as e:
                    self.logger.error(f"处理单个元素时出错: {str(e)}")
                    continue

            return True

        except Exception as e:
            self.logger.error(f"处理点击事件时出错: {str(e)}")
            return False

    def _click_element(self, x, y, double_click=False):
        """
        执行点击操作
        :param x: x坐标
        :param y: y坐标
        :param double_click: 是否双击
        """
        try:
            # 移动鼠标
            pyautogui.moveTo(x, y, duration=0.5)
            
            if double_click:
                pyautogui.doubleClick()
            else:
                pyautogui.click()

        except Exception as e:
            self.logger.error(f"点击操作失败: {str(e)}")
            raise 

    def scroll_down(self, amount=None):
        """
        向下滚动页面
        :param amount: 滚动的数量，默认为None时滚动一个页面高度
        """
        try:
            if amount is None:
                # 默认滚动一个页面高度（负值表示向下滚动）
                pyautogui.scroll(-800)
            else:
                # 使用指定的滚动量
                pyautogui.scroll(-amount)
            time.sleep(0.5)  # 等待滚动完成
            return True
        except Exception as e:
            self.logger.error(f"向下滚动失败: {str(e)}")
            return False

    def scroll_up(self, amount=None):
        """
        向上滚动页面
        :param amount: 滚动的数量，默认为None时滚动一个页面高度
        """
        try:
            if amount is None:
                # 默认滚动一个页面高度（正值表示向上滚动）
                pyautogui.scroll(800)
            else:
                # 使用指定的滚动量
                pyautogui.scroll(amount)
            time.sleep(0.5)  # 等待滚动完成
            return True
        except Exception as e:
            self.logger.error(f"向上滚动失败: {str(e)}")
            return False

# 执行点击操作
# click_result = mouse_controller.process_clicks(
#     detecting_filename, 
#     result['parsed_content']
# )
# if not click_result:
#     return jsonify({
#         'status': 'error',
#         'message': '点击操作执行失败'
#     }), 500