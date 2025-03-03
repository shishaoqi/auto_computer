import hashlib
import os
import sys
import random
import psutil
import time

# 获取文件md5
def get_file_md5(file_name):
  """
  计算文件的md5
  :param file_name:
  :return:
  """
  if os.path.exists(file_name) == False:
    return ""

  m = hashlib.md5()  #创建md5对象
  with open(file_name,'rb') as fobj:
    while True:
      data = fobj.read(4096)
      if not data:
        break
      m.update(data) #更新md5对象
  return m.hexdigest()  #返回md5对象


# 获取文件md5
def get_str_md5(str_data):
    md5_tool = hashlib.md5()
    md5_tool.update(str_data.encode("utf-8"))
    str_md5 = md5_tool.hexdigest()
    return str_md5


def get_work_dir():
    # 打包时候使用的工作目录
    cur_flile_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    # 测试时候使用的工作目录
    # cur_flile_dir = os.path.split(os.path.realpath(__file__))[0]
    return cur_flile_dir


# 获取cache目录
def get_cache_dir():
    str_cache_dir = get_work_dir() + "\\cache"
    if not os.path.isdir(str_cache_dir):
      os.mkdir(str_cache_dir)
    return str_cache_dir


# 获取img目录
def get_cache_img_dir():
    str_img_dir = get_cache_dir() + "\\img"
    if not os.path.isdir(str_img_dir):
      os.mkdir(str_img_dir)
    return str_img_dir


# 获取order_img目录
def get_cache_order_img_dir():
    str_img_dir = get_cache_dir() + "\\order_img"
    if not os.path.isdir(str_img_dir):
      os.mkdir(str_img_dir)
    return str_img_dir

# 获取driver目录
def get_driver_dir():
    str_driver_dir = get_cache_dir() + "\\driver"
    if not os.path.isdir(str_driver_dir):
      os.mkdir(str_driver_dir)
    return str_driver_dir


# 随机生成字符串
def generate_random_str(randomlength=16):
  """
  生成一个指定长度的随机字符串
  """
  random_str =''
  base_str ='abcdefghigklmnopqrstuvwxyz0123456789'
  length =len(base_str) -1
  for i in range(randomlength):
    random_str +=base_str[random.randint(0, length)]
  return random_str


# 随机生成walmart 密码
def generate_random_walmart_password():
  # 8–100 characters
  # Upper & lowercase letters
  # At least one number or special character
  random_str =''
  lower_letters ='abcdefghigklmnopqrstuvwxyz'
  upper_letters = lower_letters.upper()
  str_password = ''
  str_password += random.choice(list(lower_letters))
  str_password += random.choice(list(upper_letters))
  str_password += random.choice(list('0123456789'))
  str_password += generate_random_str(5)
  return str_password

#结束名为notepad.exe"的进程kill process by name("notepad.exe")
def kill_process_by_name(process_name):
  for process in psutil.process_iter(['pid','name']):
    if process.info['name']== process_name:
      kill_name = process_name
      cmd = f'taskkill /F /IM "{kill_name}"'
      os.system(cmd)
      # process.kill()
      print(f"Process {process_name} has been terminated.")

#结束命令
def kill_process_by_name_start_with(process_name):
  for process in psutil.process_iter(['pid','name']):
    if process.info['name'].startswith(process_name):
      kill_name = process.info['name']
      cmd = f'taskkill /F /IM "{kill_name}"'
      os.system(cmd)
      kill_name = process.info['name']
      print(f"Process {kill_name} startswith={process_name} has been terminated.")

#根据进程名获取pid list
def query_pid_list_by_name(process_name):
  pid_list = []
  for process in psutil.process_iter(['pid','name']):
    if process.info['name']== process_name:
      pid = process.info['pid']
      pid_list.append(pid)
  return pid_list

#结束pid
def kill_process_by_pid(pid):
    cmd = f'taskkill /PID {pid} /F'
    os.system(cmd)
    print(f"Process pid={pid} has been terminated.")

# 获取excel目录
def get_excel_dir():
    str_excel_dir = get_work_dir() + "\\excel"
    if not os.path.isdir(str_excel_dir):
      os.mkdir(str_excel_dir)
    return str_excel_dir

# 获取robot chat聊天目录
def get_robot_chat_cache_dir():
    str_robot_chat_dir = get_cache_dir() + "\\robot_chat"
    if not os.path.isdir(str_robot_chat_dir):
      os.mkdir(str_robot_chat_dir)
    return str_robot_chat_dir

# 获取当前时间戳
def get_current_time():
    return int(time.time())

# 获取当前时间戳
def get_current_ms_time():
    return int(time.time() * 1000)

# 替换最后一个字符串
def replace_last_string(text : str, old_str : str, new_str : str):
    text_parts = text.rsplit(old_str, 1)
    if len(text_parts) > 1:
        new_text = new_str.join(text_parts)
        return new_text
    else:
        return text