# 处理事件类别

from screenshot_processor import ScreenshotProcessor
from mouse_controller import MouseController  
from utils.logger import get_logger
import requests
import json
import time

logger = get_logger(__name__)

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
            res = upload_images(result['original_image'], result['processed_image'], prompt)
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
        self.mouse_controller.scroll(0, scroll_amount)

    def _scroll_page_down(self, scroll_amount: int = 300):
        """
        向下滚动页面
        
        Args:
            scroll_amount (int): 滚动的像素量，正数表示向下滚动，默认300像素
        """
        self.mouse_controller.scroll(0, -scroll_amount)  # 使用负值表示向下滚动

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
        img = self.screenshot_processor.screenshot()
        image_paths = [img]
        prompt = '''请识别这张截图是不是 walmart 网站的首页。提示：walmart 网站首页是什么样的呢？首先，浏览器 URL 中能看到 walmart.com; 其次，页面顶栏最左边有 walmart logo，顶栏中间部分是搜索框。注意：您的响应应遵循以下格式：{"is_walmart_page": 1}。是 walmart 网站的首页，is_walmart_page 置为 1，不是置为 0。请勿包含任何其他信息。'''
        
        res = upload_multiple_images(image_paths, prompt)
        if not res:
            return None
        json_str = res['result']
        walmart_data = json.loads(json_str)
        return walmart_data.get("is_walmart_page")
    
    def click_account_btn(self):
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 请找出网页右上角的 Account 按钮。
        #                 注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
        #     number = self.process_image_with_prompt(prompt, result, "account")
        #     if self._click_element_by_number(number, result['parsed_content']):
        #         return result['parsed_content'][number]
        #     logger.warning(f'Walmart entry with number {number} not found')
        #     return None
        bbox = [0.9097564816474915, 0.08835277706384659, 0.9547790288925171, 0.13475187122821808]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("click_account_btn 不可点击")
        self._click_element(bbox)

        return 1
    
    def enter_account(self):
        # success, result, status_code = self.screenshot_processor.process_screenshot()
        # if status_code == 200:
        #     prompt = '''我将为您提供两张图片：第一张是原始图片，第二张是在原图基础上添加了序号标注的图片。
        #                 第二张图上这些序号都被彩色方框包围，方框外就不是数字所属的部分。
        #                 请找出网页右上部的下拉框里的 Account。
        #                 注意：您的响应应遵循以下格式：{"account": 3}，3是序号。请勿包含任何其他信息。'''
            
        #     number = self.process_image_with_prompt(prompt, result, "account")
        #     if self._click_element_by_number(number, result['parsed_content']):
        #         return result['parsed_content'][number]
        #     logger.warning(f'Walmart entry with number {number} not found')
        #     return None
        bbox = [0.9104751348495483, 0.20280081033706665, 0.9731246829032898, 0.2321944534778595]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("enter_account 不可点击")
        self._click_element(bbox)
        return 1

    def click_account_setting(self):
        bbox = [0.2549503445625305, 0.8525451421737671, 0.3763135075569153, 0.8972681760787964]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("account_setting 不可点击")  # 抛出异常

        self._click_element(bbox)
        time.sleep(1)
        self.mouse_controller.scroll_down(400)
        return 1

    def click_address(self):
        bbox = [0.2665168344974518, 0.745004415512085, 0.37486201524734497, 0.7754677534103394]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("click_address 不可点击")
        self._click_element(bbox)
        return 1

    def after_create_address_enter_wallet(self):
        bbox = [0.25586557388305664, 0.4200286865234375, 0.37026968598365784, 0.45071613788604736]
        if not self._wait_for_clickable_element(bbox, 3):
            raise Exception("after_create_address_enter_wallet Wallet link 不可点击")
        self._click_element(bbox)

        # 点击 Credi/debit card
        card_bbox = [0.4318029284477234, 0.3831401467323303, 0.4449518322944641, 0.4026656150817871]
        if not self._wait_for_clickable_element(card_bbox, 6):
            raise Exception("after_create_address_enter_wallet card_bbox 不可点击")
        self._click_element(card_bbox)

        return 1

    def click_add_address(self):
        time.sleep(0.8)
        bbox = [0.38615599274635315, 0.28405794501304626, 0.42059326171875, 0.30172109603881836]
        if not self._wait_for_clickable_element(bbox):
            raise Exception("click_add_address 不可点击")
        self._click_element(bbox)
        time.sleep(1.35)
        self.mouse_controller.scroll_down(80)
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

        time.sleep(3)
        return 1

    def fill_wallet_form(self, account_info):
        logger.info(f'account_info={account_info}')
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
        # Monthly radio 
        bbox = [0.5029519200325012, 0.31222501397132874, 0.5149767994880676, 0.33702735772132874]
        if not self._wait_for_clickable_element(bbox, 5):
            raise Exception("Monthly radio 不可点击")
        self._click_element(bbox)

        # I agree to the terms
        bbox = [0.35335153341293335, 0.7572852373123169, 0.3656124472618103, 0.7804934978485107]
        if not self._wait_for_clickable_element(bbox, 5):
            raise Exception("'I agree to the terms' 不可点击")
        self._click_element(bbox)

        # Start free 30-day trial Btn
        bbox = [0.5494832992553711, 0.8027747273445129, 0.6348459124565125, 0.837860643863678]
        if not self._wait_for_clickable_element(bbox, 3):
            raise Exception("Start free 30-day trial Btn 不可点击")
        self._click_element(bbox)
        time.sleep(3)
        return 1

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

def upload_images(original_image_path, processed_image_path, prompt, api_url="http://192.168.11.250:8004/analyze"):
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

def upload_multiple_images(image_paths: list, prompt: str, api_url: str = "http://192.168.11.250:8004/analyze"):
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