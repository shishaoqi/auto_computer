from mouse_controller import MouseController  
from utils.logger import get_logger
import pyautogui
import time

logger = get_logger(__name__)

class Fill_action:
    def __init__(self, mouse_controller: MouseController) -> None:
        self.mouse_controller = mouse_controller


    def input_ele(self, bbox: list, val: str):
        """处理输入框元素"""
        self._click_element(bbox)
        
        # 输入文本
        self.mouse_controller.type_text(val)
        time.sleep(0.5)  # 等待输入完成

    def input_ele_by_shiftLeft(self, bbox: list, val: str):
        """处理输入框元素"""
        self._click_element_by_shiftLeft(bbox, 100)
        
        # 输入文本
        self.mouse_controller.type_text(val)
        time.sleep(0.5)  # 等待输入完成

    def checkbox_ele(self, bbox: list):
        """处理复选框元素"""
        self._click_element(bbox)

    def btn_ele(self, bbox: list):
        """处理按钮元素"""
        self._click_element(bbox)
        # 需要 - 再定位与选择


    def select_ele(self, bbox: list, val: str, form_ele: str):
        """处理下拉选择框元素"""
        if form_ele == "address_state":
            for key in range(59):
                pyautogui.press('up')
                time.sleep(0.06)
        elif form_ele == "wallet_state":
            for key in range(59):
                pyautogui.press('up')
                time.sleep(0.06)
            pass

        self._click_element(bbox)
        
        # 输入选项值并回车确认
        self.mouse_controller.type_text(val)
        # self.mouse_controller.press_enter()
        time.sleep(0.5)  # 等待选择完成

    def _click_element(self, bbox: list) -> bool:
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        rel_x = (bbox[0] + bbox[2]) / 2
        rel_y = (bbox[1] + bbox[3]) / 2
        self.mouse_controller.move_to(rel_x, rel_y)
        self.mouse_controller.click(rel_x, rel_y)
        time.sleep(0.5)

    # x 轴左移 left px
    def _click_element_by_shiftLeft(self, bbox: list, left: int) -> bool:
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        rel_x = (bbox[0] + bbox[2]) / 2 - left
        rel_y = (bbox[1] + bbox[3]) / 2
        self.mouse_controller.move_to(rel_x, rel_y)
        self.mouse_controller.click(rel_x, rel_y)
        time.sleep(0.5)

