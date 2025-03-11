from PIL import Image
import pyautogui
import time
from utils.logger import get_logger
from utils.cursor import get_cursor_info, identify_cursor, CURSOR_SHOWING

class MouseController:
    def __init__(self):
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.25  # 每个操作之间的延迟
        self.logger = get_logger(__name__)

    def click(self, bbox: list):
        """
        执行点击操作，将相对坐标转换为实际屏幕坐标
        :param bbox: 边界框坐标 [x1, y1, x2, y2]
        """
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 计算中心点坐标
            rel_x = (bbox[0] + bbox[2]) / 2
            rel_y = (bbox[1] + bbox[3]) / 2
            # 将相对坐标转换为实际屏幕坐标
            actual_x = int(rel_x * screen_width)
            actual_y = int(rel_y * screen_height)
            
            # 执行点击
            self._click_element(actual_x, actual_y)
            
            return True
        except Exception as e:
            self.logger.error(f"点击操作失败: {str(e)}")
            return False
    
    def actual_click(self, actual_x, actual_y):
        """
        执行点击操作，将相对坐标转换为实际屏幕坐标
        :param bbox: 边界框坐标 [x1, y1, x2, y2]
        """
        try:
            # 执行点击
            self._click_element(actual_x, actual_y)
            
            return True
        except Exception as e:
            self.logger.error(f"点击操作失败: {str(e)}")
            return False
    
    def click_bbox(self, bbox: list) -> bool:
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        rel_x = (bbox[0] + bbox[2]) / 2
        rel_y = (bbox[1] + bbox[3]) / 2
        self.move(rel_x, rel_y)
        self.click(bbox)
        time.sleep(0.15)

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
            pyautogui.moveTo(x, y, duration=0.76)
            
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

    def move(self, rel_x, rel_y):
        """
        移动鼠标到指定的相对坐标
        :param rel_x: x轴相对坐标(0-1范围)
        :param rel_y: y轴相对坐标(0-1范围)
        """
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 将相对坐标转换为实际屏幕坐标
            actual_x = int(rel_x * screen_width)
            actual_y = int(rel_y * screen_height)
            
            # 移动鼠标
            pyautogui.moveTo(actual_x, actual_y, duration=2.1)
            return True
        except Exception as e:
            self.logger.error(f"移动鼠标失败: {str(e)}")
            return False

    def move_to(self, bbox: list):
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        rel_x = (bbox[0] + bbox[2]) / 2
        rel_y = (bbox[1] + bbox[3]) / 2
        self.move(rel_x, rel_y)

    # 打字输入
    def type_text(self, val: str):
        pyautogui.write(val, interval=0.35)

    def press_enter(self):
        """
        执行按下回车键的操作
        """
        try:
            pyautogui.press('enter')  # 按下回车键
        except Exception as e:
            self.logger.error(f"按下回车键失败: {str(e)}")

    def get_cursor_type(self):
        """获取当前光标类型"""
        try:
            cursor_info = get_cursor_info()
            if cursor_info.flags & CURSOR_SHOWING:
                return identify_cursor(cursor_info.hCursor)
            else:
                return "No cursor"
        except Exception as e:
            print(f"获取光标类型失败: {str(e)}")
            return "Unknown cursor"

    def element_is_clickable(self, bbox: list) -> bool:
        """
        检测指定的bbox区域是否包含可点击的元素，通过检查鼠标悬停时的光标变化
        
        Args:
            bbox (list): 要检测的区域坐标 [x1, y1, x2, y2]
            
        Returns:
            bool: 如果区域包含可点击元素返回True，否则返回False
        """
        # 计算区域中心点
        rel_x = (bbox[0] + bbox[2]) / 2
        rel_y = (bbox[1] + bbox[3]) / 2
        
        # 移动鼠标到目标位置
        original_cursor = self.get_cursor_type()
        self.move(rel_x, rel_y)
        time.sleep(0.15)  # 等待光标更新
        
        # 获取当前光标类型
        try:
            current_cursor = self.get_cursor_type()
            self.logger.info(f'current_cursor = {current_cursor}  ----------------111')
        except Exception as e:
            self.logger.error(f'获取光标类型失败: {str(e)}')
            return False
        
        # 检查光标是否变为手型或其他表示可点击的类型
        is_clickable = current_cursor in ['OCR_HAND']
        
        return is_clickable
    
    def move_relative(self, dx, dy):
        """
        从当前位置相对移动鼠标
        :param dx: x轴相对移动距离(像素)
        :param dy: y轴相对移动距离(像素)
        """
        try:
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 计算新位置
            new_x = current_x + dx
            new_y = current_y + dy
            
            # 移动鼠标到新位置
            pyautogui.moveTo(new_x, new_y, duration=0.3)
            return [new_x, new_y]
        except Exception as e:
            self.logger.error(f"相对移动鼠标失败: {str(e)}")
            return []

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