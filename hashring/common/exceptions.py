# -*- coding: utf-8 -*-


class ErrorNotImplemented(Exception):
    u"""接口未实现.

    Note：这个异常类只是示例，实际接口未实现是可以直接抛NotImplemented这个内置异常的。
    """
    def __str__(self):
        return "接口未实现！"


class ErrorFileOpenFailed(Exception):
    u"""文件打开错误.
    """
    def __str__(self):
        return "文件打开错误！"


class ErrorFileSaveFailed(Exception):
    u"""文件保存错误.
    """
    def __str__(self):
        return "文件保存错误！"


class ErrorInvalidParam(Exception):
    u"""参数无效错误.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "无效的参数：%s，请检查后重试！".format(self.msg)
