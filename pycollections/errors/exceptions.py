class ConstantError(TypeError):
    pass


class AccessDeniedError(AttributeError):
    pass


class LockedListError(AccessDeniedError):
    pass


class UnlockedListError(ValueError):
    pass


class InvalidOperation(Exception):
    pass
