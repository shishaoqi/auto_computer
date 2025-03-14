import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # 新增：加载.env文件

# 确保日志目录存在
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

class DailyRotatingFileHandler(TimedRotatingFileHandler):
    def __init__(self, log_dir):
        self.log_dir = log_dir
        # 获取当前日期作为文件名
        filename = self._get_log_filename()
        super().__init__(
            filename=filename,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )

    def _get_log_filename(self):
        return os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    def doRollover(self):
        """重写文件滚动方法，使用新的日期作为文件名"""
        if self.stream:
            self.stream.close()
            self.stream = None
        # 更新文件名为新的日期
        self.baseFilename = self._get_log_filename()
        if not self.delay:
            self.stream = self._open()

def get_logger(name, log_dir="log"):
    # 创建文件处理器
    file_handler = DailyRotatingFileHandler(log_dir)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    
    # 设置日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - [%(filename)s] %(lineno)d |-|  %(message)s',
        datefmt='%H:%M:%S,%f'[:-3]
    )
    
    # 为handler设置格式
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 配置日志
    logger = logging.getLogger(name)
    # 禁用向上传播到根日志记录器
    logger.propagate = False # 控制台仍然有日志输出，这是因为Python logging的默认行为。要完全禁用控制台输出，我们需要禁止日志消息向上传播到根日志记录器（root logger）
    log_level = os.getenv("LOG_LEVEL", "DEBUG")  # 从环境变量获取日志级别，默认为DEBUG
    logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)  # 开启控制台输出
    
    return logger
