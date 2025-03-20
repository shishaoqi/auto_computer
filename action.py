# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from mouse_controller import MouseController  
from utils.logger import get_logger
from browser import Browser
import pyautogui
import requests
import json
import time

logger = get_logger(__name__)

class BBoxNotClickableException(Exception):
    """自定义异常类，用于表示 bbox 不可点击的情况"""
    pass

class OpenPageFail(Exception):
    """自定义异常类，用于表示打开网页失败的情况"""
    pass

class Action:
    def __init__(self, screenshot_processor: ScreenshotProcessor, mouse_controller: MouseController) -> None:
        self.screenshot_processor = screenshot_processor
        self.mouse_controller = mouse_controller

    # 绑定收货地址
    def bind_address():
        pass

    # 创建银行卡或信用卡
    def create_bankCard():
        pass

    # 填写登录表单
    def login():
        pass

    def process_image_with_prompt(self, prompt: str, result: dict, expected_key: str):
        """
        处理图片并获取AI响应
        
        Args:
            prompt (str): 发送给AI的提示词
            result (dict): 包含原始和处理后图片路径的字典
            expected_key (str): 期望从AI响应中获取的键名
            
        Returns:
            Any: AI响应中指定键的值，如果处理失败则返回None
        """
        try:
            res = self.upload_images(result['original_image'], result['processed_image'], prompt)
            if not res:
                return None
            json_str = res['result']
            response_data = json.loads(json_str)
            return response_data.get(expected_key)
        except Exception as e:
            logger.error(f'处理图片失败: {str(e)}')
            return None

    def _click_element_by_number(self, number: int, parsed_content: list) -> bool:
        """
        根据序号点击元素的通用方法
        
        Args:
            number (int): 要点击元素的序号
            parsed_content (list): 解析后的内容列表
            
        Returns:
            bool: 点击是否成功
        """
        if number is None or not parsed_content:
            return False
            
        if 0 <= number < len(parsed_content):
            entry = parsed_content[number]
            logger.info(entry)
            if 'bbox' in entry:
                # bbox格式: [x1, y1, x2, y2]，取中点的相对坐标
                self.mouse_controller.click(entry['bbox'])
                return True
        return False
    
    def _is_clickable_element(self, bbox: list) -> bool:
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
        original_cursor = self.mouse_controller.get_cursor_type()
        self.mouse_controller.move(rel_x, rel_y)
        time.sleep(0.15)  # 等待光标更新
        
        # 获取当前光标类型
        try:
            current_cursor = self.mouse_controller.get_cursor_type()
            logger.info(f'current_cursor = {current_cursor}  ----------------111')
        except Exception as e:
            logger.error(f'获取光标类型失败: {str(e)}')
            return False
        
        # 检查光标是否变为手型或其他表示可点击的类型
        is_clickable = current_cursor in ['OCR_HAND']
        
        return is_clickable

    def _click_element(self, bbox: list) -> bool:
        """
        点击指定bbox区域的元素
        
        Args:
            bbox (list): 要点击的区域坐标 [x1, y1, x2, y2]
            
        Returns:
            bool: 点击是否成功
        """ 
        self.mouse_controller.click(bbox)
        return True

    def _scroll_page_up(self, scroll_amount: int = 300):
        """
        向上滚动页面
        
        Args:
            scroll_amount (int): 滚动的像素量，正数表示向上滚动，默认300像素
        """
        self.mouse_controller.scroll_up(0, scroll_amount)

    def _scroll_page_down(self, scroll_amount: int = 300):
        """
        向下滚动页面
        
        Args:
            scroll_amount (int): 滚动的像素量，正数表示向下滚动，默认300像素
        """
        self.mouse_controller.scroll_down(0, scroll_amount)  # 使用负值表示向下滚动

    def _scroll_down_page(self, scroll_times: int = 1, scroll_amount: int = 300, delay: float = 0.5):
        """
        向下滚动页面指定次数
        
        Args:
            scroll_times (int): 滚动次数，默认为1次
            scroll_amount (int): 每次滚动的像素量，默认300像素
            delay (float): 每次滚动之间的延迟时间(秒)，默认0.5秒
        """
        for _ in range(scroll_times):
            self._scroll_page_down(scroll_amount)
            time.sleep(delay)

    def check_is_walmart_plus(self, account_info):
        time.sleep(3)
        bbox_home_account = [0.9097564816474915, 0.08835277706384659, 0.9547790288925171, 0.13475187122821808]
        bbox_walmart_plus = [0.9120470285415649, 0.1770082712173462, 0.9745729565620422, 0.20471949875354767]
        if not self._wait_for_clickable_element(bbox_home_account):
            prompt = '''这是打开 Walmart 网站首页的截图，请判断页面是否正常打开。打开失败的情况有：1. 页面加载不完全  2. 页面显示内容为 "This site can't be reached"
            注意：您的响应应遵循以下格式：正常打开返回{"status": "success"}, 打开失败返回{"status": "fail"}。请勿包含任何其他信息。'''
            
            status = self._process_screenshot_with_prompt(prompt, "status")
            logger.info(f'当前页面打开状态是{status}')

            if status == "success":
                raise BBoxNotClickableException("bbox_home_account_btn 不可点击")
            else:
                raise OpenPageFail("walmart 页面打不开")
                
        self._click_element(bbox_home_account)
        time.sleep(0.46)
        self._click_element(bbox_walmart_plus)

        time.sleep(4)
        for i in range(2):
            time.sleep(4.5)
            prompt = '''请通过这图浏览器截图判断当前用户是否已开通 Walmart+。判断方法： 如果页面内容中包含 "Your Walmart+ benefits" 或 "Manage membership",那么就可以判断为已开通 Walmart+。其它情况，统统可归类为未开通 Walmart+。
            注意：您的响应应遵循以下格式：已开通 Walmart+ 返回 {"is_walmart_plus": 1}；未开通 Walmart+ 返回 {"is_walmart_plus": 0}。请勿包含任何其他信息。'''
            
            is_walmart_plus = self._process_screenshot_with_prompt(prompt, "is_walmart_plus")
            if is_walmart_plus == 1:
                b = Browser()
                b.close_browser(account_info['ads_id'])
                break
        
        if is_walmart_plus == 0:
            walmart_home = [0.015906335785984993, 0.08713185787200928, 0.05957440286874771, 0.13244634866714478]
            if self._wait_for_clickable_element(walmart_home):
                self._click_element(walmart_home)
            time.sleep(2.8)

        return is_walmart_plus

    def find_walmart(self):
        # 处理截图
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 请找出被标注的蓝色 Walmart 官网链接的序号。这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 注意：您的响应应遵循以下格式：{"walmart": 3}，3 是序号。请勿包含任何其他信息。'''
            
        #     walmart_number = self.process_image_with_prompt(prompt, result, "walmart")
            
        #     # 从 result['parsed_content'] 中遍历找出第 walmart_number 个的数据
        #     if self._click_element_by_number(walmart_number, result['parsed_content']):
        #         return result['parsed_content'][walmart_number]
            
        #     logger.warning(f'Walmart entry with number {walmart_number} not found')
        #     return None
            
        # else:
        #     logger.error('find_walmart error')

        # 第一次截图获取的坐标
        bbox = [0.08867187798023224, 0.29027777910232544, 0.16875000298023224, 0.3125]
        
        click_able = self._is_clickable_element(bbox)
        if click_able:
            self._click_element(bbox)
        else:
            # 第二次截图获取的坐标
            bbox = [0.08749999850988388, 0.2680555582046509, 0.21250000596046448, 0.2923611104488373]
            click_able = self._is_clickable_element(bbox)
            if click_able == False:
                logger.warning(f'区域 {bbox} 不包含可点击元素')
                raise Exception("不可点击")  # 抛出异常
            self._click_element(bbox)

        return 1


    def is_walmart_page(self):
        """Check if the current page is the Walmart homepage"""
        prompt = '''请识别这张截图是不是 walmart 网站的首页。提示：walmart 网站首页是什么样的呢？首先，浏览器 URL 中能看到 walmart.com; 其次，页面顶栏最左边有 walmart logo，顶栏中间部分是搜索框。注意：您的响应应遵循以下格式：{"is_walmart_page": 1}。是 walmart 网站的首页，is_walmart_page 置为 1，不是置为 0。请勿包含任何其他信息。'''
        
        return self._process_screenshot_with_prompt(prompt, "is_walmart_page")
    
    def click_account_btn(self):
        """Click the account button in the header"""
        i = 0
        while True:
            bbox = [0.9097564816474915, 0.08835277706384659, 0.9547790288925171, 0.13475187122821808]
            if not self._wait_for_clickable_element(bbox):
                # Check if page loaded correctly
                prompt = '''这是打开 Walmart 网站首页的截图，请判断页面是否正常打开。打开失败的情况有：1. 页面加载不完全  2. 页面显示内容为 "This site can't be reached"
                注意：您的响应应遵循以下格式：正常打开返回{"status": "success"}, 打开失败返回{"status": "fail"}。请勿包含任何其他信息。'''
                
                status = self._process_screenshot_with_prompt(prompt, "status")
                logger.info(f'当前页面打开状态是{status}')

                if status == "success":
                    raise BBoxNotClickableException("click_account_btn 不可点击")
                else:
                    raise OpenPageFail("walmart 页面打不开")
                    
            self._click_element(bbox)

            bbox_account = [0.9104751348495483, 0.20280081033706665, 0.9731246829032898, 0.2321944534778595]
            if (not self._wait_for_clickable_element(bbox_account)) and i == 0: # 可能是有弹窗，点击一下
                self._click_element(bbox_account)
                i += 1
                continue
            elif not self._wait_for_clickable_element(bbox_account):
                # raise Exception("enter_account 不可点击")
                continue
            else:
                self._click_element(bbox_account)
                break

        return 1
    
    def enter_account(self):
        for i in range(2):
            bbox = [0.9104751348495483, 0.20280081033706665, 0.9731246829032898, 0.2321944534778595]
            if not self._wait_for_clickable_element(bbox) and i == 0: # 可能是有弹窗，点击一下
                self._click_element(bbox)
            elif not self._wait_for_clickable_element(bbox):
                raise Exception("enter_account 不可点击")
        self._click_element(bbox)

        return 1

    def click_account_setting(self):
        """Navigate to account settings"""
        bbox = [0.2549503445625305, 0.8525451421737671, 0.3763135075569153, 0.8972681760787964]
        self._click_when_clickable(bbox, error_message="account_setting 不可点击")
        time.sleep(1)
        self.mouse_controller.scroll_down(400)
        return 1

    def click_address(self):
        bbox = [0.2665168344974518, 0.745004415512085, 0.37486201524734497, 0.7754677534103394]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("click_address 不可点击")
        self._click_element(bbox)
        return 1

    def after_create_address_enter_wallet(self, account_info):
        bbox = [0.25586557388305664, 0.4200286865234375, 0.37026968598365784, 0.45071613788604736]
        if not self._wait_for_clickable_element(bbox, 3):
            raise BBoxNotClickableException("after_create_address_enter_wallet Wallet link 不可点击")
        self._click_element(bbox)

        time.sleep(6)

        while True:
            # 处理找不到添加卡的链接
            # 判断是否已添加卡
            prompt = '''这是一张浏览器界面的截图。首先，判断页面是不是加载完整，如果未加载完整，则直接返回 {"number": -1}。接着，在页面中查找 "Payment methods"后面的括号里的哪个数字，该数字表示有 n 张卡。
            注意：您的响应应遵循以下格式：{"number": n}, n 是表示数字。例如：{"number": 5}，其中 5 表示紧接于 "Payment methods" 后面的括号里的是 5。没有找到 "Payment methods"，而是找到 "Add a payment method"，则返回 {"number": 0}。请勿包含任何其他信息。'''

            number = self._process_screenshot_with_prompt(prompt, "number")
            logger.info(f'当前帐户已经绑定{number}张卡')
            if number != -1:
                break
            time.sleep(3.5)
        if number == 1:
            prompt = '''这是一张浏览器界面的截图。页面中，在 "Credit or debit card(1)" 下面是一张卡的信息，请获取 "Card ending in" 后面的四个数字。
            注意：您的响应应遵循以下格式：{"card_number": 4308}，4308 是在"Card ending in" 后面的那四个数字'''

            card_number = self._process_screenshot_with_prompt(prompt, "card_number")
            logger.info(f'卡号后四位是 {card_number}')
            if account_info['cardcode'][-4:] == str(card_number):
                return 206
        
        while number > 0:
            add_new_payment_method = [0.3855791687965393, 0.3159421384334564, 0.4854893684387207, 0.35353779792785645]
            self.mouse_controller.move_to(add_new_payment_method)
            check_1 = self.mouse_controller.get_cursor_type()
            edit_btn = [0.4730468690395355, 0.4504449665546417, 0.5025107860565186, 0.4814169108867645]
            self.mouse_controller.move_to(edit_btn)
            check_2 = self.mouse_controller.get_cursor_type()

            self._click_element(edit_btn)
            time.sleep(2.5)
            self.mouse_controller.scroll_down(900)

            del_card_btn = [0.617047905921936, 0.5675092935562134, 0.672519326210022, 0.6057189702987671]
            if self._wait_for_clickable_element(del_card_btn, 4):
                del_card_btn = [0.617047905921936, 0.5675092935562134, 0.672519326210022, 0.6057189702987671]
                self._click_element(del_card_btn)
                confirm_btn = [0.5271917581558228, 0.5723111629486084, 0.5703563690185547, 0.6032514572143555]
                self._click_element(confirm_btn)
            elif self._wait_for_clickable_element([0.6169742345809937, 0.6176642775535583, 0.6727732419967651, 0.6560440063476562], 3):
                del_card_btn = [0.6169742345809937, 0.6176642775535583, 0.6727732419967651, 0.6560440063476562]
                self._click_element(del_card_btn)
                confirm_btn = [0.5271917581558228, 0.5723111629486084, 0.5703563690185547, 0.6032514572143555]
                self._click_element(confirm_btn)
            elif self._wait_for_clickable_element([0.6171774864196777, 0.6802083253860474, 0.6726424098014832, 0.7184507846832275], 3):
                del_card_btn = [0.6171774864196777, 0.6802083253860474, 0.6726424098014832, 0.7184507846832275]
                self._click_element(del_card_btn)
                confirm_btn = [0.5271917581558228, 0.5723111629486084, 0.5703563690185547, 0.6032514572143555]
                self._click_element(confirm_btn)

                
                time.sleep(3)
                number -= 1
                pyautogui.press('f5')

        time.sleep(6)
        # 点击 Credi/debit card
        card_bbox = [0.4318029284477234, 0.3831401467323303, 0.4449518322944641, 0.4026656150817871]
        if not self._wait_for_clickable_element(card_bbox, 6):
            raise BBoxNotClickableException("after_create_address_enter_wallet card_bbox 不可点击")
        self._click_element(card_bbox)

        return 1

    def click_add_address(self, account_info):
        time.sleep(2.8)
        # 判断是否已添加地址
        for i in range(3):
            prompt = '''这是一张浏览器界面的截图，请查看主页内容中，Addresses 标题下有几个地址列表。如果页面还没加载中，返回 {"address_count": -1} 。
            注意：您的响应应遵循以下格式：{"address_count": n}, n 是数字。例如：{"address_count": 5}，其中 5 表示有5个地址。请勿包含任何其他信息。'''   
            address_count = self._process_screenshot_with_prompt(prompt, "address_count")
            logger.info(f'当前帐户有{address_count}个地址')
            if address_count > -1:
                break
            time.sleep(3.5)

        if address_count == 1:
            prompt = '''这是一张浏览器界面的截图，Addresses 标题之下是地址信息（在 +Add address 下面），请获取地址相关的所有数据。
            注意：您的响应应遵循以下格式：{"address": "address_info"}，请用地址信息替换掉 address_info。如果没有找到地址信息，返回 {"address": ""}。请勿包含任何其他信息。'''
            address = self._process_screenshot_with_prompt(prompt, "address")
            address = address.lower()
            logger.info(f'address === {address}')
            if account_info['address'].lower() in address:
                return 205
            
            logger.info(f"{account_info['first_name'].lower()} ---- {account_info['city'].lower()} ------------ {account_info['zip_code']}")
            if account_info['first_name'].lower() in address and account_info['city'].lower() in address and account_info['zip_code'] in address:
                return 205
        
        while address_count > 0:
            remove_btn = [0.7072377800941467, 0.32699310779571533, 0.7346668839454651, 0.35097432136535645]
            self._click_element(remove_btn)
            time.sleep(0.6)
            del_confirm_btn = [0.5277529358863831, 0.5654923915863037, 0.5699787735939026, 0.5957998633384705]
            self._click_element(del_confirm_btn)
            time.sleep(2)
            pyautogui.press('f5')
            address_count -= 1
            time.sleep(6)

        bbox = [0.38615599274635315, 0.28405794501304626, 0.42059326171875, 0.30172109603881836]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("click_add_address 不可点击")
        self._click_element(bbox)
        time.sleep(1.35)
        
        return 1

    def click_wallet(self):
        time.sleep(0.7)
        bbox = [0.25694137811660767, 0.7728841304779053, 0.3740352988243103, 0.8032107949256897]
        self._click_element(bbox)
        time.sleep(4)

    def fill_address_form(self, account_info):
        logger.info(f'account_info={account_info}')
        from forms.fill_address import Fill_address
        fa = Fill_address(account_info)
        fa.fill()

        time.sleep(3.5)

        for i in range(2):
            # 识别是否创建地址信息成功
            prompt = '''这是一张浏览器界面的截图，请查看主页内容，识别是否创建地址信息成。判断依据为: 如果页面上有“Your address was successfully added” 表示创建成功，其它情况都是失败的。
            注意：您的响应应遵循以下格式：成功返回 {"result": "success", "msg": ""}, 失败返回 {"result": "fail", "msg": "描述情况"}，msg 是用来记录失败时页面在描述什么。请勿包含任何其他信息。'''

            re = self._process_screenshot_with_prompt(prompt)
            logger.info(f'创建地址信息结果为 {re}')
            result = re.get("result")
            if result == "success":
                break
            time.sleep(3)

        if result == "fail":
            msg = re.get("msg")
            use_suggested_addr = [0.4289628863334656, 0.6256446242332458, 0.5703867077827454, 0.65202397108078]
            entered_addr = [0.4644531309604645, 0.6638888716697693, 0.536328136920929, 0.6840277910232544]
            self.mouse_controller.move_to(use_suggested_addr)
            use_suggested_addr_cursor = self.mouse_controller.get_cursor_type()
            self.mouse_controller.move_to(entered_addr)
            entered_addr_cursor = self.mouse_controller.get_cursor_type()
            if use_suggested_addr_cursor == 'OCR_HAND' and entered_addr_cursor == 'OCR_HAND':
                self.mouse_controller.click(entered_addr)

        return 1

    def fill_wallet_form(self, account_info):
        from forms.fill_wallet import Fill_wallet
        fw = Fill_wallet(account_info)
        fw.fill()

        time.sleep(8)
        self.mouse_controller.scroll_up(900)
        return 1
    
    def start_fress_30_day_trial(self):
        time.sleep(3)
        self.mouse_controller.scroll_up(900)

        # 点击 Account
        bbox = [0.2558051645755768, 0.172993004322052, 0.3718321919441223, 0.21351772546768188]
        if not self._wait_for_clickable_element(bbox, 3):
            raise Exception("Account list_btn 不可点击")
        self._click_element(bbox)

        time.sleep(1)
        # walmart plux 
        bbox = [0.2725761830806732, 0.2666454017162323, 0.370516836643219, 0.29633238911628723]
        if not self._wait_for_clickable_element(bbox, 3):
            raise Exception("walmart+ link 不可点击")
        self._click_element(bbox)
        time.sleep(4.5)
            
        # start your free 30-day trial 
        bbox = [0.23940591514110565, 0.4323989748954773, 0.3389694094657898, 0.46798384189605713]
        if not self._wait_for_clickable_element(bbox, 5):
            raise Exception("walmart plux link 不可点击")
        self._click_element(bbox)


        time.sleep(5)
        self.mouse_controller.scroll_up(800)

        bbox = [0.5030820965766907, 0.37992063164711, 0.5154772996902466, 0.40166175365448]
        if self._wait_for_clickable_element(bbox, 5):
            # First time start membership
            # Monthly radio 
            if not self._wait_for_clickable_element(bbox, 5):
                raise Exception("Monthly radio 不可点击")
            self._click_element(bbox)

            for i in range(2):
                # I agree to the terms
                bbox = [0.35335153341293335, 0.7572852373123169, 0.3656124472618103, 0.7804934978485107]
                if not self._wait_for_clickable_element(bbox, 5):
                    # raise Exception("'I agree to the terms' 不可点击")
                    if i == 0:
                        self._scroll_page_down(50)
                    continue
                self._click_element(bbox)

            # Start free 30-day trial Btn
            bbox = [0.5494832992553711, 0.8027747273445129, 0.6348459124565125, 0.837860643863678]
            if not self._wait_for_clickable_element(bbox, 3):
                raise Exception("Start free 30-day trial Btn 不可点击")
            self._click_element(bbox)
        elif self._wait_for_clickable_element([0.5029519200325012, 0.31222501397132874, 0.5149767994880676, 0.33702735772132874], 5):
            # Restart your membership
            # Monthly radio 
            bbox = [0.5029519200325012, 0.31222501397132874, 0.5149767994880676, 0.33702735772132874]
            if not self._wait_for_clickable_element(bbox, 5):
                raise Exception("Monthly radio 不可点击")
            self._click_element(bbox)

            # I agree to the terms
            bbox =  [0.35320946912765503, 0.7014710903167725, 0.36595773696899414, 0.724168062210083]
            if not self._wait_for_clickable_element(bbox, 5):
                raise Exception("'I agree to the terms' 不可点击")
            self._click_element(bbox)

            # Rejoin Walmart+
            bbox = [0.564965546131134, 0.7476170063018799, 0.6348819732666016, 0.7828387022018433]
            if not self._wait_for_clickable_element(bbox, 3):
                raise Exception("Start free 30-day trial Btn 不可点击")
            self._click_element(bbox)
        else:
            raise Exception("寻找 Monthly radio 失败")

        time.sleep(5)

        return 1
    
    def join_walmart_plus_result(self, account_info):
        """Check if Walmart+ subscription was successfully activated"""
        prompt = '''这是一张浏览器界面的截图，请查看图片内容判断是否成功开通 Walmart+。
        判断依据：
            1. 如果页面中有 "You're now part of Walmart+"，则表示开通成功，
            2. 没有找到 "You're now part of Walmart+"，就是开通失败，又可以分为 右侧弹窗报异常与其它情况（未知）。
        注意：您的响应应遵循以下格式：成功开通返回 {"resut": "success", "msg": ""}, 右侧弹窗报异常返回 {"resut": "window_error", "msg": "描述弹窗情况"}, 其它情况（未知） {"resut": "other", "msg": "描述情况"}。其中，msg 指的是把发生情况描述出来。请勿包含任何其他信息。'''
        
        for i in range(3):
            re = self._process_screenshot_with_prompt(prompt, "resut")
            if not re:
                raise Exception("Error: join_walmart_plus_result response error")
            logger.info(f'join_walmart_plus_result == {re}, in {i+1}')
            if re == "success":
                b = Browser()
                b.close_browser(account_info['ads_id'])
                break
            time.sleep(4.5)
        
        return re

    def _process_screenshot_with_prompt(self, prompt, expected_key=None, max_retries=1):
        """
        Take a screenshot, process it with the given prompt, and extract the expected key
        
        Args:
            prompt (str): The prompt to send to the vision model
            expected_key (str, optional): The key to extract from the response
            max_retries (int): Number of retries if processing fails
            
        Returns:
            The value of the expected key, or the entire parsed data if no key specified
        """
        for _ in range(max_retries):
            try:
                img = self.screenshot_processor.screenshot()
                image_paths = [img]
                
                res = self.upload_multiple_images(image_paths, prompt)
                if not res:
                    logger.error("Failed to get response from vision model")
                    continue
                    
                json_str = res['result']
                data = json.loads(json_str)
                
                if expected_key:
                    return data.get(expected_key)
                return data
                
            except Exception as e:
                logger.error(f"Error processing screenshot: {str(e)}")
                if _ < max_retries - 1:  # Don't sleep on the last iteration
                    time.sleep(3)
        
        return None

    def logging(self, account_info):
        """Check if user is logged in and handle login if needed"""
        prompt = '''这张图是Walmart页面截图，请根据这张图来判断当前有无帐户登录是否。判断依据：1. 页面右上角如果有  Sign In Account 或 页面内容主体里靠下边的部分有 Sign in or create account，那么说明是没有登录帐户。 2. 如果页面右上角是 Hi xxxx，那么说明是有登录帐户。注意：您的响应应遵循以下格式：有登录帐户返回 {"is_logging": 1}。无帐户登录返回 {"is_logging": 0}。请勿包含任何其他信息。'''
        
        is_logging = self._process_screenshot_with_prompt(prompt, "is_logging")
        if is_logging == 1:
            return {'logging': 1}
        else:
            # 执行登录操作
            return {'logging': 0}
        

    def _wait_for_clickable_element(self, bbox: list, max_attempts: int = 8, wait_time: float = 3) -> bool:
        """
        等待指定的bbox区域变为可点击元素
        
        Args:
            bbox (list): 要检测的区域坐标 [x1, y1, x2, y2]
            max_attempts (int): 最大尝试次数，默认为5
            wait_time (float): 每次尝试之间的等待时间（秒），默认为3秒
            
        Returns:
            bool: 如果区域变为可点击元素返回True，否则返回False
        """
        click_able = self._is_clickable_element(bbox)
        attempts = 0
        while not click_able and attempts < max_attempts:
            time.sleep(wait_time)
            click_able = self._is_clickable_element(bbox)
            attempts += 1
        return click_able

    def upload_images(self, original_image_path, processed_image_path, prompt, api_url="http://192.168.11.250:8004/analyze"):
        """
        上传原始图片和处理后的图片到服务器
        
        Args:
            original_image_path (str): 原始图片的路径
            processed_image_path (str): 处理后图片的路径
            prompt (str): 提示词
            api_url (str): API端点URL，默认为http://localhost:8004/analyze
            
        Returns:
            dict: 服务器返回的响应
        """
        # 获取文件扩展名
        original_ext = original_image_path.split('.')[-1]
        processed_ext = processed_image_path.split('.')[-1]
        
        # 准备文件
        files = [
            ('images', ('image1.' + original_ext, open(original_image_path, 'rb'), f'image/{original_ext}')),
            ('images', ('image2.' + processed_ext, open(processed_image_path, 'rb'), f'image/{processed_ext}'))
        ]
        
        # 准备数据
        data = {
            "prompt": prompt
        }
        
        try:
            # 发送请求
            response = requests.post(api_url, files=files, data=data)
            response.raise_for_status()  # 检查响应状态
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"上传失败: {str(e)}")
            return None
        finally:
            # 确保文件被正确关闭
            for _, (_, file_obj, _) in files:
                file_obj.close()

    def upload_multiple_images(self, image_paths: list, prompt: str, api_url: str = "http://192.168.11.250:8004/analyze"):
        """
        上传多张图片到服务器
        
        Args:
            image_paths (list): 图片路径列表
            prompt (str): 提示词
            api_url (str): API端点URL，默认为http://192.168.11.250:8004/analyze
            
        Returns:
            dict: 服务器返回的响应
        """
        # 准备文件
        files = []
        try:
            for idx, image_path in enumerate(image_paths, 1):
                # 获取文件扩展名
                ext = image_path.split('.')[-1]
                # 添加文件到列表
                files.append(
                    ('images', (f'image{idx}.{ext}', open(image_path, 'rb'), f'image/{ext}'))
                )
            
            # 准备数据
            data = {
                "prompt": prompt
            }
            
            # 发送请求
            response = requests.post(api_url, files=files, data=data)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"上传失败: {str(e)}")
            return None
        
        finally:
            # 确保所有文件被正确关闭
            for _, (_, file_obj, _) in files:
                file_obj.close()

    def _click_when_clickable(self, bbox, max_attempts=8, wait_time=3, error_message=None):
        """
        Wait for an element to become clickable and then click it
        
        Args:
            bbox (list): The bounding box coordinates [x1, y1, x2, y2]
            max_attempts (int): Maximum number of attempts to check clickability
            wait_time (float): Time to wait between attempts
            error_message (str): Custom error message if element is not clickable
            
        Returns:
            bool: True if clicked successfully
            
        Raises:
            BBoxNotClickableException: If the element is not clickable after max attempts
        """
        if not self._wait_for_clickable_element(bbox, max_attempts, wait_time):
            if error_message:
                raise BBoxNotClickableException(error_message)
            else:
                raise BBoxNotClickableException(f"Element at {bbox} is not clickable")
        
        return self._click_element(bbox)

    def _check_page_state(self, prompt, expected_key, expected_value=None):
        """
        Check the current page state using the vision model
        
        Args:
            prompt (str): The prompt to send to the vision model
            expected_key (str): The key to extract from the response
            expected_value: The expected value for the key
            
        Returns:
            bool: True if the page state matches the expected state
        """
        result = self._process_screenshot_with_prompt(prompt, expected_key)
        if expected_value is not None:
            return result == expected_value
        return result is not None