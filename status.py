class Status:
    # 成功
    STATUS_SUCCEED = 0

    # 未登录
    STATUS_LOGOUT = 11

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

    # 代理失败
    STATUS_AGENT_FAIL = 27


    # ###创建会员
    # 创建会员失败
    STATUS_MEMBERSHIP_CREATE_UNKNOW_ERROR = 6000