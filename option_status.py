#操作状态
class OPTION_STATUS(object):

    # 取消成功
    STATUS_SUCCEED = 0

    # 登录失败
    STATUS_LOGIN_ERROR = 12

    # 账号锁住了
    STATUS_ACCOUNT_LOCKED_ERROR = 13

    # 登录失败 输入密码错误
    STATUS_ACCOUNT_PASSWORD_ERROR = 14

    # 登录时候 获取邮箱验证码错误
    STATUS_EMAIL_ERROR = 15

    # 登录 邮箱获取验证码登录认证失败
    STATUS_EMAIL_AUTH_ERROR = 16

    # 网络错误
    STATUS_NET_ERROR = 18

    # ads启动失败
    STATUS_ADS_START_ERROR = 19

    # ads id不存在
    STATUS_ADS_ID_NOT_EXSIT_ERROR = 20

    # 网络错误 网络会一直加载This page isn’t working
    STATUS_PAGE_NOT_WORKING_NET_ERROR = 21

    # 需要人机验证
    STATUS_ROBOT_ERROR = 22

    # 账号给关闭了
    STATUS_ACCOUNT_CLOSED_ERROR = 23

    # 登录时候 需要邮箱认证但是没有邮箱密码
    STATUS_LOGIN_NO_EMAIL_PASSWORD_ERROR = 24

    # 登录密码为空无法登录
    STATUS_LOGIN_NO_ACCOUNT_PASSWORD_ERROR = 25

    # 账号尚未注册
    STATUS_ACCOUNT_NO_REGISTERED_ERROR = 26

    # ###会员取消相关
    # 本身已经不是会员了
    STATUS_IS_NOT_MEMBERSHIP = 1000
    # 剩余时间充足不执行取消
    STATUS_NOT_OP_TIME = 1001
    # 取消会员操作失败-未知错误
    STATUS_MEMBERSHIP_UNKNOW_ERROR = 1002

    # ###订单相关
    # 订单原本已经是取消状态了
    STATUS_ORDER_IS_CANCELED_ERROR = 100
    # 订单取消失败-未知错误
    STATUS_ORDER_CANCEL_UNKNOW_ERROR = 101
    # 传的订单id为空
    STATUS_ORDER_ID_IS_NULL_ERROR = 102
    # 订单id不存在
    STATUS_ORDER_ID_NOT_EXSIT_ERROR = 103
    # 进入订单界面失败
    STATUS_ORDER_PAGE_ENTER_ERROR = 104
    # 进入订单详情界面失败
    STATUS_ORDER_DETAIL_PAGE_ENTER_ERROR = 105
    # 订单当前状态无法取消
    STATUS_ORDER_CAN_NOT_CANCELED_ERROR = 106

    # ###机器人聊天相关
    # 机器人聊天未知错误
    STATUS_ROBOT_CHAT_UNKNOW_ERROR = 2000
    # 账号没聊天权限
    STATUS_ROBOT_CHAT_NO_PERMISSION_ERROR = 2001
    # 聊天未知中断错误
    STATUS_ROBOT_CHAT_UNKNOW_INTERRUPT_ERROR = 2002
    # 进入聊天界面失败
    STATUS_ROBOT_CHAT_ENTER_CHAT_PAGE_ERROR = 2003
    # 发送消息失败
    STATUS_ROBOT_CHAT_SEND_MSG_ERROR = 2004
    # 机器人结束通话
    STATUS_ROBOT_CHAT_ROBOT_END_COMMUNICATE_ERROR = 2005
    # 机器人挂了无法链接
    STATUS_ROBOT_CHAT_ROBOT_DIE_ERROR = 2006
    # walmart主动结束聊天
    STATUS_ROBOT_CHAT_WALMART_END_COMMUNICATE_ERROR = 2007

    # ###聊天管理相关
    # 聊天未知错误
    STATUS_CHAT_NONE = 3000
    # 聊天启动中
    STATUS_CHAT_START_ING = 3001
    # 聊天未知错误
    STATUS_CHAT_UNKNOW_ERROR = 3002
    # 进入聊天界面失败
    STATUS_CHAT_ENTER_CHAT_PAGE_ERROR = 3003

    # ###爬取手机号码相关
    # 抓取手机号码失败
    STATUS_GET_PHONE_NUMBER_UNKNOW_ERROR = 4000

    # ###修改邮箱相关
    # 修改邮箱失败
    STATUS_CHANGE_EMAIL_UNKNOW_ERROR = 5000