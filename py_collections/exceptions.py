# Exceptions classes for PyCollection 0.2.0

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

