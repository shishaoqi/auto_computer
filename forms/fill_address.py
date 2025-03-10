from mouse_controller import MouseController 
import time
from utils.logger import get_logger

ADDRESS_FORM = {
    "first_name":   ["", "input", [0.38270068168640137, 0.2930210828781128, 0.6542178392410278, 0.3367534279823303]],
    "last_name":    ["", "input", [0.3827262818813324, 0.3556141257286072, 0.6540148854255676, 0.3975934386253357]],
    "address":      ["", "input+enter", [0.3827870488166809, 0.4166955351829529, 0.653272807598114, 0.4587864875793457]],
    "city":         ["", "input", [0.3831089735031128, 0.5378350019454956, 0.6548876762390137, 0.5809253454208374]],
    "province":     ["", "select", [0.3842995762825012, 0.5997611284255981, 0.5197539329528809, 0.6413083076477051]], # 对应表单 State
    "zip_code":     ["", "input", [0.5204119682312012, 0.5995507836341858, 0.6514458656311035, 0.6412823796272278]],
    "phone_number": ["", "input", [0.3832525610923767, 0.6608595848083496, 0.6540420651435852, 0.7047080993652344]],
}

logger = get_logger(__name__)

class Fill_address:
    def __init__(self, account_info) -> None:
        from forms.fill_form_action import Fill_action
        
        self.mouse_controller = MouseController()
        self.fill_action = Fill_action(mouse_controller=self.mouse_controller)
        self.account_info = account_info
        # Update ADDRESS_FORM values with account_info
        global ADDRESS_FORM
        for field_name in ADDRESS_FORM:
            if field_name in account_info:
                ADDRESS_FORM[field_name][0] = account_info[field_name]

        
    def fill(self):
        """遍历填写地址表单"""
        for field_name, (value, ele_type, bbox) in ADDRESS_FORM.items():
            logger.info(f"Filling {field_name}: {value}")
            
            if ele_type == "input":
                self.fill_action.input_ele(bbox, value)
            elif ele_type == "input+enter":
                self.fill_action.input_ele_endby_enter(bbox, value)
            elif ele_type == "select":
                self.fill_action.select_ele(bbox, value, "address_state")
            elif ele_type == "checkbox":
                self.fill_action.checkbox_ele(bbox)
            elif ele_type == "button":
                self.fill_action.btn_ele(bbox)
            else:
                logger.warning(f"Unknown element type: {ele_type} for {field_name}")
            
            # 每个字段填写后稍作等待
            time.sleep(0.6)
        
        # 点击  More delivery instructions
        bbox = [0.38673561811447144, 0.8793678283691406, 0.39610129594802856, 0.8966156840324402]
        self.mouse_controller.click_bbox(bbox)

        # 点击 Save 按钮
        time.sleep(0.8)
        bbox = [0.6177930235862732, 0.906648576259613, 0.6507642269134521, 0.936152458190918]
        self.mouse_controller.click_bbox(bbox)

        # 检测是否成功提交
        # 1. 检测是否有弹窗：Unable to verify address
        # 2. 如果成功的是什么样子的

        # 1
        # x_btn = [0.5547648668289185, 0.39693883061408997, 0.573358416557312, 0.43435168266296387] # 关闭按钮
        # yes = [0.4287818968296051, 0.5957921147346497, 0.570303738117218, 0.6225367188453674]
        no = [0.4248208999633789, 0.6264414191246033, 0.5720537304878235, 0.6544809937477112]
        three_eles = [[0.5547648668289185, 0.39693883061408997, 0.573358416557312, 0.43435168266296387], [0.4287818968296051, 0.5957921147346497, 0.570303738117218, 0.6225367188453674], [0.4248208999633789, 0.6264414191246033, 0.5720537304878235, 0.6544809937477112]]
        cursor_list = []
        for i, ele in enumerate(three_eles):
            self.mouse_controller.move_to(ele)
            cursor_type = self.mouse_controller.get_cursor_type() 
            cursor_list.append(cursor_type)
        
        count = 0
        for type in cursor_list:
            if type == "OCR_HAND":
                count += 1

        # 2
        if count < 3:
            logger.info('----- Success save address info -----')
            pass
        else:
            self.mouse_controller.click_bbox(no)
            # 记录写入数据库
            logger.warn(f"Unable to verify address ---- {self.account_info}")
            pass

