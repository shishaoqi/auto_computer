from mouse_controller import MouseController 
import time
from utils.logger import get_logger

logger = get_logger(__name__)
WALLET_FORM = {
    "cardcode":     ["", "input", [0.39894309639930725, 0.35750240087509155, 0.4148775637149811, 0.38952094316482544]],
    "first_name":   ["", "input", [0.3940892815589905, 0.41731399297714233, 0.5608780384063721, 0.46148690581321716]],
    "last_name":    ["", "input", [0.561921238899231, 0.417435884475708, 0.7295187711715698, 0.46195492148399353]],
    #MM  YY   "valid_date": "0328",
    "cvv":          ["", "input-shift_left", [0.5450897216796875, 0.5747315287590027, 0.5551998019218445, 0.5956715941429138]], # 要左移 100
    "phone_number": ["", "input", [0.5641240477561951, 0.5620772242546082, 0.6485218405723572, 0.6076893210411072]],
    "address":      ["", "input", [0.39455023407936096, 0.6507920026779175, 0.6257587671279907, 0.6944865584373474]],
    "city":         ["", "input", [0.5110426545143127, 0.7117041945457458, 0.6226527690887451, 0.7554894089698792]],
    "province":     ["", "select", [0.39539146423339844, 0.7739880084991455, 0.5073491334915161, 0.8167343139648438]], # State
    "zip_code":     ["", "input", [0.5111494660377502, 0.7738559246063232, 0.6224389672279358, 0.8164272904396057]],
}

class Fill_wallet:
    def __init__(self, account_info) -> None:
        from forms.fill_form_action import Fill_action
        
        mouse_controller = MouseController()
        self.fill_action = Fill_action(mouse_controller=mouse_controller)

        # Update ADDRESS_FORM values with account_info
        global WALLET_FORM
        for field_name in WALLET_FORM:
            if field_name in account_info:
                WALLET_FORM[field_name][0] = account_info[field_name]

        
    def fill(self):
        """遍历填写地址表单"""
        for field_name, (value, ele_type, bbox) in WALLET_FORM.items():
            logger.info(f"Filling {field_name}: {value}")
            
            if ele_type == "input":
                self.fill_action.input_ele(bbox, value)
            elif ele_type == "input-shift_left":
                self.fill_action.input_ele(bbox, value)
            elif ele_type == "select":
                self.fill_action.select_ele(bbox, value, "wallet_state")
            elif ele_type == "checkbox":
                self.fill_action.checkbox_ele(bbox)
            elif ele_type == "button":
                self.fill_action.btn_ele(bbox)
            else:
                logger.warning(f"Unknown element type: {ele_type} for {field_name}")
            
            # 每个字段填写后稍作等待
            time.sleep(0.5)