from mouse_controller import MouseController 
import time
from utils.logger import get_logger

logger = get_logger(__name__)
WALLET_FORM = {
    "cardcode":     ["", "input", [0.39848795533180237, 0.3562644422054291, 0.5593876481056213, 0.3896193206310272]],
    "first_name":   ["", "input", [0.3940923511981964, 0.41753268241882324, 0.5608288049697876, 0.46136611700057983]],
    "last_name":    ["", "input", [0.5619645118713379, 0.4175584614276886, 0.7294825315475464, 0.4617365598678589]],
    #MM  YY   "valid_date": "0328",
    "MM":           ["", "select-MM", [0.3941483795642853, 0.49658483266830444, 0.5605353116989136, 0.5393311381340027]],
    "YY":           ["", "select-YY", [0.5688033699989319, 0.5076108574867249, 0.5803123712539673, 0.5309964418411255]],
    "cvv":          ["", "input-shift_left", [0.5450670719146729, 0.5751372575759888, 0.5551005005836487, 0.595954418182373]], # 要左移 240
    "phone_number": ["", "input", [[0.5640407800674438, 0.5624861121177673, 0.6482664346694946, 0.6075438857078552], [0.5640352964401245, 0.5053229331970215, 0.6486218571662903, 0.5500961542129517]]],
    # "address":      ["", "input", [0.39455023407936096, 0.6507920026779175, 0.6257587671279907, 0.6944865584373474]],
    # "city":         ["", "input", [0.5110426545143127, 0.7117041945457458, 0.6226527690887451, 0.7554894089698792]],
    # "province":     ["", "select", [0.39539146423339844, 0.7739880084991455, 0.5073491334915161, 0.8167343139648438]], # State
    # "zip_code":     ["", "input", [0.5111494660377502, 0.7738559246063232, 0.6224389672279358, 0.8164272904396057]],
}

class Fill_wallet:
    def __init__(self, account_info) -> None:
        from forms.fill_form_action import Fill_action
        
        self.mouse_controller = MouseController()
        self.fill_action = Fill_action(mouse_controller=self.mouse_controller)

        # Update ADDRESS_FORM values with account_info
        global WALLET_FORM
        for field_name in WALLET_FORM:
            if field_name in account_info:
                WALLET_FORM[field_name][0] = account_info[field_name]
        WALLET_FORM["MM"][0] = account_info["valid_date"][0:2]
        WALLET_FORM["YY"][0] = account_info["valid_date"][2:4]

        
    def fill(self):
        """遍历填写地址表单"""
        for field_name, (value, ele_type, bbox) in WALLET_FORM.items():
            logger.info(f"Filling {field_name}: {value}")
            
            if ele_type == "input":
                self.fill_action.input_ele(bbox, value)
            elif ele_type == "input-shift_left":
                self.fill_action.input_ele_by_shiftLeft(bbox, value)
            elif ele_type == "select":
                self.fill_action.select_ele(bbox, value, "wallet_state")
            elif ele_type == "select-MM":
                self.fill_action.select_ele(bbox, value, "wallet_MM")
            elif ele_type == "select-YY":
                self.fill_action.select_ele(bbox, value, "wallet_YY")
            elif ele_type == "checkbox":
                self.fill_action.checkbox_ele(bbox)
            elif ele_type == "button":
                self.fill_action.btn_ele(bbox)
            else:
                logger.warning(f"Unknown element type: {ele_type} for {field_name}")
            
            # 每个字段填写后稍作等待
            time.sleep(0.5)

        # 点击 Save 按钮
        time.sleep(0.36)
        bbox = [0.6793497204780579, 0.7256332635879517, 0.7290651202201843, 0.7609488368034363]
        self.mouse_controller.click_bbox(bbox)
            
        