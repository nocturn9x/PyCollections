from from py_collections import exceptions
import inspect

# TODO -> Add docstrings and document

class Const:

    def __init__(self):
        self.__d = dict()

    @property
    def __dict__(self):
        raise AccessDeniedError("Access Denied")

    def __contains__(self, key):
        dict.__contains__(self.__d, key)

    def __setattr__(self, key, value):
        if inspect.stack()[1][3] != "__init__":
            if isinstance(value, int) or isinstance(value, float):
                if key in self.__d:
                    raise ConstantError(
                        f"cannot reassign values for constants, value for {key} is already {self.__d[key]}")
                else:
                    self.__d[key] = value
            else:
                raise TypeError("constant's value MUST be numeric")

        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        if dict.__contains__(self.__d, key):
            return self.__d[key]
        else:
            raise AttributeError(f"object of type '{type(self)}' has no attribute '{key}'")

    def __dir__(self):
        raise AccessDeniedError("Access Denied")
