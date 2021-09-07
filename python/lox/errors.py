import lark


class LoxRuntimeError(Exception):
    def __init__(self, token: lark.Token, message: str):
        self.token = token
        self.message = message


class LoxResolutionError(Exception):
    def __init__(self, token: lark.Token, message: str):
        self.token = token
        self.message = message
