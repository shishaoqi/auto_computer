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
        if len(bbox) == 4:
            for i in range(5):
                self.mouse_controller.move_to(bbox)
                current_cursor = self.mouse_controller.get_cursor_type()
                if current_cursor != 'OCR_IBEAM':
                    time.slpeep(0.4)
                    continue
                else:
                    break

            self.mouse_controller.click(bbox)
            
            # 清空现有内容
            pyautogui.hotkey('ctrl', 'a')  # 全选现有文本
            pyautogui.press('delete')      # 删除选中内容
            time.sleep(0.2)                # 短暂等待清空完成

            # 输入文本
            self.mouse_controller.type_text(val)
            time.sleep(0.5)  # 等待输入完成
        elif len(bbox) == 2:
            found = False
            for i, b in enumerate(bbox):
                self.mouse_controller.move_to(b)
                current_cursor = self.mouse_controller.get_cursor_type()
                if current_cursor != 'OCR_IBEAM':
                    continue
            
                self.mouse_controller.click(b)
                # 清空现有内容
                pyautogui.hotkey('ctrl', 'a')  # 全选现有文本
                pyautogui.press('delete')      # 删除选中内容
                time.sleep(0.2)                # 短暂等待清空完成

                # 输入文本
                self.mouse_controller.type_text(val)
                time.sleep(0.5)  # 等待输入完成
                found = True

            if not found:
                raise Exception('input ele not found')

    def input_ele_endby_enter(self, bbox: list, val: str):
        """处理输入框元素"""
        self._click_element(bbox)

        # 清空现有内容
        pyautogui.hotkey('ctrl', 'a')  # 全选现有文本
        pyautogui.press('delete')      # 删除选中内容
        time.sleep(0.2)                # 短暂等待清空完成
        
        # 输入文本
        self.mouse_controller.type_text(val)
        time.sleep(5)
        pyautogui.press("enter")
        time.sleep(0.5)  # 等待输入完成

    def input_ele_by_shiftLeft(self, bbox: list, val: str):
        """处理输入框元素"""
        self._click_element_by_shiftLeft(bbox, 240)

        # 清空现有内容
        pyautogui.hotkey('ctrl', 'a')  # 全选现有文本
        pyautogui.press('delete')      # 删除选中内容
        time.sleep(0.2)                # 短暂等待清空完成
        
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
        self._click_element(bbox)
        state_list = ['State', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'AA', 'AP', 'AE', 'AS', 'GU', 'MP', 'PR', 'VI']

        state_idx =  [ 0,        1,   2,    3,     4,   5,     6,    7,    8,    9,   10,   11,   12,   13,   14,   15,    16,  17,   18,   19,     20,    21,   22,  23,   24,    25,   26,   27,   28,   29,   30,   31,   32,  33,   34,   35,   36,    37,  38,   39,   40,   41,    42,    43,    44,   45,   46,  47,    48,   49,   50,   51,   52,   53,   54,   55,   56,   57,   58,   59]
        if form_ele == "address_state":
            for key in range(59):
                pyautogui.press('up')
            # self._click_element_by_shiftUp(100)
            # for i in range(4):
            #     self.mouse_controller.scroll_up(185)
            #     time.sleep(0.26)
            idx = 0
            for i, s in enumerate(state_list):
                if s == val:
                    idx = i
            for key in range(idx):
                pyautogui.press('down')
        elif form_ele == "wallet_state":
            for key in range(59):
                pyautogui.press('up')
        elif form_ele == "wallet_MM":
            mm_list = ['MM', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
            for i, s in enumerate(mm_list):
                if s == val:
                    break
                else:
                    pyautogui.press('down')
        elif form_ele == "wallet_YY":
            yy_list = ['YY', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44']
            for i, s in enumerate(yy_list):
                if s == val:
                    break
                else:
                    pyautogui.press('down')
        else:
            pass
        
        # 输入选项值并回车确认
        # self.mouse_controller.type_text(val)
        self.mouse_controller.press_enter()
        time.sleep(0.2)  # 等待选择完成

    def _click_element(self, bbox: list) -> bool:
        # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
        self.mouse_controller.move_to(bbox)
        self.mouse_controller.click(bbox)
        time.sleep(0.5)

    # x 轴左移 left px
    def _click_element_by_shiftLeft(self, bbox: list, left: int) -> bool:
        self.mouse_controller.move_to(bbox)
        [actual_x, actual_y] = self.mouse_controller.move_relative(-left, 0)  # 向左移动left像素
        self.mouse_controller.actual_click(actual_x, actual_y)  # 在当前位置点击
        time.sleep(0.3)
        
    # y 轴上移 up px
    def _click_element_by_shiftUp(self, up: int) -> bool:
        self.mouse_controller.move_relative(0, -up)  # 向上移动up像素
        time.sleep(0.3)

