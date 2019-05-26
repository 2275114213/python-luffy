


class BaseResponse(object):
    def __init__(self):
        self.code=1000
        self.msg="购物车添加成功"
        self.data=None
    @property
    def dict(self):
        return self.__dict__


