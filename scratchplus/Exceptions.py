class ScratchException(Exception):
    pass


class ScratchAuthException(ScratchException):
    pass


class ScratchNoAuthException(ScratchAuthException):
    pass


class ScratchLoginException(ScratchAuthException):
    pass


class ScratchForumException(ScratchException):
    pass
