import threading
from .errors.exceptions import *
from ast import literal_eval as make_collection


class ConstantDict(dict):
    """This class implements a 'constant' (or immutable) Mapping, we'll face
       those apexes in a second.

       ConstantDict inherits most of its functions
       from Python's built-in Mapping objects: dicts.
       This mapping mostly behaves like an usual python dict,
       except for  4 things:

          - Once a key-value pair is inserted, it cannot be removed anymore
          - Existing key-value pairs cannot be overwritten
          - Attempting to access object.__dict__ will fail
          - Attempting to access dir(object) will fail

       These characteristics have been specifically implemented
       to avoid item's accidental overwrite/deletion.

       Let's face the apexes at the beginning: In pure Python,
       it's impossible to implement an immutable container as
       it is duck typed: tuples and frozen sets, for example,
       are implemented in C AND Python, this allowing them
       to be truly immutable.

       You might be wondering, "Soo, how does this class even
       exists? Didn't you just say it's impossible?!"

       Yeah, it is, and actually this mapping is not truly
       immutable: it just overwrites any known standard method
       to access mappings values and edit them, but it is still
       possible to edit those values by accessing the class
       attribute via {object}_ConstantDict__container.

       This mapping is indeed intended to reduce the probability of ACCIDENTALLY overwriting those
       values, if you are looking for immutable objects natively, just
       switch to Java :)"""

    def __init__(self):
        """Initializes self"""

        self.as_dict = False
        self.__container = dict()  # This attribute MUST NOT BE TOUCHED

    def __dir__(self):
        """Overrides dir(object)"""

        raise AccessDeniedError("Access Denied")

    @property
    def __dict__(self):
        """This method (actually, a property) forbids the user to access
           the '__dict__' property, attribute of any python object

           Overriding the __dict__ attribute with a property
           ensures that the ConstantDict values remain unchanged"""

        raise AccessDeniedError("Access Denied")

    @property
    def __class__(self):
        """This property returns the type of the ConstantDict.

           The class is built so that it can emulate Python dicts,
           see below 'typeof' property for more detailed info"""

        if self.as_dict:
            return type(self.__container)
        else:
            return type(self)

    @property
    def typeof(self):
        """The ConstantDict class is built so that it can emulate
           Python dicts, by manipulating the value returned by the __class__ parameter

           To pass isinstance() check, use ConstantDict.typeof() as first argument, after
           having called act_as_dict() on the container"""

        return self.__class__

    def act_as_dict(self):
        """Bound method to activate/deactivate Python dict emulation.

           See 'typeof' and '__class__' properties for more info"""

        if self.as_dict:
            self.as_dict = False
        else:
            self.as_dict = True
        return self.as_dict

    def __delitem__(self, key):
        """Overrides the standard __delitem__ dunder method for dicts,
           disallowing the user to perform actions such as:

           >>> d = ConstantDict()
           >>> d["foo"] = "bar"
           >>> d
              {'foo':'bar'}
           >>> del d["foo"]
             raises  Error"""

        raise InvalidOperation("Operation not permitted")

    def __setitem__(self, key, value):
        """Overrides the standard __setitem__ bound method for dicts,
           disallowing the user to edit already existing values inside the container"""

        if key in self.__container:
            raise ConstantError(f"Cannot overwrite existing key. Value for '{key}' is already '{self.__container[key]}'")
        else:
            self.__container[key] = value

    def __iter__(self):
        return self.__container.__iter__()

    def __getitem__(self, key):
        return self.__container.__getitem__(key)

    def __len__(self):
        return self.__container.__len__()

    def __contains__(self, item):
        return self.__container.__contains__(item)

    def __repr__(self):
        return str(self.__container)


class NamedTuple(tuple):
    """This class implement a named tuple, that is, a container that behaves like a
    common tuple, but has named arguments.

    The tuple works as described below:

    - Create tuple :
        >>> test = NamedTuple(key1='var1', key2='var2', ...)

    - Find element in tuple :
        >>> test.find(key1)
        'var1'

    - Get tuple keys :
        >>> test.keys()
        [key1, key2, ...]

    - Get tuple elements :
        >>> test.items()
        ['var1', 'var2', ...]
    """

    def __init__(self, **kwargs):
        """Initializes self"""

        self.kwargs = kwargs
        self._container = None  # Tuple to be initialized yet
        self._dict = dict()  # Here the key-word couples arguments will be stored
        self._indexes = dict()  # Numerical indexes for every item in the tuple are saved with their keyword
        self._as_tuple = False
        if kwargs:
            for key, value in kwargs.items():
                if isinstance(value, str) and "<" in value:
                    kwargs[key] = value.replace("<", "$")
            self.formatted_args = "("
            for index, key in enumerate(kwargs):
                if isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                    if not index + 1 == len(kwargs):
                        self.formatted_args += f"{key}={kwargs[key]}/"
                    else:
                        self.formatted_args += f"{key}={kwargs[key]}"
                elif isinstance(kwargs[key], tuple) or isinstance(kwargs[key], list) or isinstance(kwargs[key], set) or isinstance(kwargs[key], dict):
                    if not index + 1 == len(kwargs):
                        self.formatted_args += f"<{key}={kwargs[key]}/"
                    else:
                        self.formatted_args += f"<{key}={kwargs[key]}"
                elif isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                    if not index + 1 == len(kwargs):
                        self.formatted_args += f"{key}={kwargs[key]}/"
                    else:
                        self.formatted_args += f"{key}={kwargs[key]}"
                else:
                    if not index + 1 == len(kwargs):
                        self.formatted_args += f"{key}='{kwargs[key]}'/"
                    else:
                        self.formatted_args += f"{key}='{kwargs[key]}'"
            self.formatted_args += ")"
            self.create_tuple()
        else:
            self.formatted_args = "()"

    def create_tuple(self):
        """This function memorizes all the required
        information for the container to work properly"""

        iter_args = self.formatted_args[1:-1].split("/")
        for arg in iter_args:
            if arg and "<" in arg:
                from_index = arg.find("=") + 1
                key = arg[0:from_index - 1].replace("<", "")
                self._dict[key] = make_collection(arg[from_index:])
            elif arg:
                try:
                    key, value = arg.split("=")
                except ValueError:
                    break
                if value.isdigit():
                    value = int(value)
                elif self.isfloat(value):
                    value = self.isfloat(value)
                self._dict[key] = value
        self._container = tuple(item[1] for item in self._dict.items())
        for item in self._dict.items():
            self._indexes[item[0]] = self._container.index(item[1])

    @staticmethod
    def isfloat(value):  # Thanks to https://www.geeksforgeeks.org/python-check-for-float-string/
        if value.replace('.', '', 1).isdigit():
            return float(value)
        else:
            return False

    def __str__(self):
        return self.formatted_args.replace("<", "").replace("$", "<").replace("/", ", ")

    def __repr__(self):
        return self

    def __getitem__(self, index):
        if isinstance(index, int):
            return self._container[index]
        elif index in self._indexes:
            return self._dict[index]
        else:
            raise IndexError("item or index not in tuple")

    def __iter__(self):
        return self._container.__iter__()

    def __contains__(self, item):
        return self._container.__contains__(item)

    def __len__(self):
        return self._container.__len__()

    def __copy__(self):
        return self._container

    def find(self, item):
        """This function finds an element inside the tuple,
        given its key"""

        if item in self._indexes:
            return self._indexes[item]
        else:
            raise KeyError("item not in tuple")

    def keys(self):
        """This function returns all the keys inside the tuple"""

        return list(self._dict.keys())

    def items(self):
        """This function returns all the values inside the tuple"""

        return list(self._dict.items())

    @property
    def __class__(self):
        """This property returns the type of the NamedTuple.

           The class is built so that it can emulate Python lists,
           see below 'typeof' property for more detailed info"""

        if self._as_tuple:
            return type(self._container)
        else:
            return type(self)

    @property
    def typeof(self):
        """The NamedTuple class is built so that it can emulate
           Python lists, by manipulating the value returned by the __class__ parameter

           To pass isinstance() check, use NamedTuple.typeof() as first argument,
           after having called act_as_tuple() on the container"""

        return self.__class__

    def act_as_tuple(self):
        """Bound method to activate/deactivate Python tuple emulation.

           See 'typeof' and '__class__' properties for more info"""

        if self._as_tuple:
            self._as_tuple = False
        else:
            self._as_tuple = True
        return self._as_tuple


class LockedList(list):

    def __init__(self, *args):
        self._container = [*args]
        self._status = False  # Initialized to unlocked state
        self._as_list = False

    def __getitem__(self, item):
        if not self._status:
            return self._container.__getitem__(item)
        else:
            raise LockedListError("list is locked")

    def __getattribute__(self, item):
        return super().__getattribute__(item)

    def __delitem__(self, item):
        if not self._status:
            return self._container.__delitem__(item)
        else:
            raise LockedListError("list is locked")

    def __add__(self, other):
        return self._container.__add__(other)

    def __mul__(self, other):
        return self._container.__add__(other)

    def __iadd__(self, other):
        return self._container.__iadd__(other)

    def __imul__(self, other):
        return self._container.__imul__(other)

    def __reversed__(self):
        return self._container.__reversed__()

    def append(self, item):
        if not self._status:
            self._container.append(item)
        else:
            raise LockedListError("list is locked")

    def lock(self):
        """Locks the list"""

        if not self._status:
            self._status = True
            return True
        else:
            raise InvalidOperation("list is already locked")

    def unlock(self):
        """Unlocks the list"""

        if self._status:
            self._status = False
            return True
        else:
            raise UnlockedListError("list is not locked")

    @property
    def status(self):
        """Returns the value of self._status"""

        return self._status

    def extend(self, iterable):
        if not self._status:
            self._container.extend(iterable)
        else:
            raise LockedListError("list is locked")

    def __iter__(self):
        if not self._status:
            return self._container.__iter__()
        else:
            raise LockedListError("list is locked")

    def __contains__(self, item):
        return self._container.__contains__(item)

    def __len__(self):
        return self._container.__len__()

    def __copy__(self):
        return self._container

    def __str__(self):
        return str(self._container)

    def __repr__(self):
        return str(self._container)

    @property
    def __class__(self):
        """This property returns the type of the LockedList.

           The class is built so that it can emulate Python lists,
           see below 'typeof' property for more detailed info"""

        if self._as_list:
            return type(self._container)
        else:
            return type(self)

    @property
    def typeof(self):
        """The LockedList class is built so that it can emulate
           Python lists, by manipulating the value returned by the __class__ parameter

           To pass isinstance() check, use LockedList.typeof() as first argument,
           after having called act_as_list() on the container"""

        return self.__class__

    def act_as_list(self):
        """Bound method to activate/deactivate Python list emulation.

           See 'typeof' and '__class__' properties for more info"""

        if self._as_list:
            self._as_list = False
        else:
            self._as_list = True
        return self._as_list

    def index(self, value, start=0, stop=9223372036854775807):
        if not self._status:
            return self._container.index(value, start, stop)
        else:
            raise LockedListError("list is locked")


class RLockedList(LockedList):

    def __init__(self, *args):
        super().__init__(*args)
        self._owner = None

    @property
    def owner(self):
        """Returns the value of self._owner"""

        return self._owner

    @property
    def status(self):
        """Returns the value of self._status"""

        return self._status

    def extend(self, iterable):
        if not self._status:
            self._container.extend(iterable)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.extend(iterable)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __getitem__(self, item):
        if not self._status:
            return self._container.__getitem__(item)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__getitem__(item)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __getattribute__(self, item):
        if not self._status:
            return self._container.__getattribute__(item)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__getattribute__(item)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __delitem__(self, item):
        if not self._status:
            return self._container.__delitem__(item)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__delitem__(item)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __add__(self, other):
        if not self._status:
            return self._container.__add__(other)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__add__(other)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __mul__(self, other):
        return self._container.__add__(other)

    def __iadd__(self, other):
        return self._container.__iadd__(other)

    def __imul__(self, other):
        if not self._status:
            return self._container.__imul__(other)
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__imul__(other)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __reversed__(self):
        if not self._status:
            return self._container.__reversed__()
        else:
            if threading.current_thread().name == self._owner:
                return self._container.__reversed__()
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def append(self, item):
        if not self._status:
            self._container.append(item)
            if threading.current_thread().name == self._owner:
                return self._container.append(item)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def index(self, value, start=0, stop=9223372036854775807):
        if not self._status:
            return self._container.index(value, start, stop)
        else:
            if self._owner == threading.current_thread().name:
                return self._container.index(value, start, stop)
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def acquire(self):
        """Acquires the container, disallowing access to the list's items
        to any thread except for the owner"""

        if self._owner is None:
            self._status = True
            self._owner = threading.current_thread().name
        else:
            raise InvalidOperation(f"thread '{self._owner}' didn't release the container yet")

    def release(self):
        """Releases the container, allowing access to the list's items globally"""

        if not self._status:
            raise InvalidOperation("container is un-acquired")
        else:
            self._owner = None
        if threading.current_thread().name == self._owner:
            if self._status:
                self._status = False
                self._owner = None
            else:
                raise InvalidOperation("container is un-acquired")
        else:
            raise InvalidOperation(f"cannot release, '{threading.current_thread().name}' is not the container owner")

    def __iter__(self):
        if not self._status:
            return self._container.__iter__()
        else:
            if self._owner == threading.current_thread().name:
                return self._container.__iter__()
            else:
                raise AccessDeniedError(f"thread '{threading.current_thread().name}' is not the container owner")

    def __str__(self):
        return super().__str__()

    @property
    def __class__(self):
        """This property returns the type of the LockedList.

           The class is built so that it can emulate Python lists,
           see below 'typeof' property for more detailed info"""

        if self._as_list:
            return type(self._container)
        else:
            return type(self)

    @property
    def typeof(self):
        """The RLockedList class is built so that it can emulate
           Python lists, by manipulating the value returned by the __class__ parameter

           To pass isinstance() check, use LockedList.typeof() as first argument, after
           having called act_as_list() on the container"""

        return self.__class__

    def act_as_list(self):
        """Bound method to activate/deactivate Python list emulation.

           See 'typeof' and '__class__' properties for more info"""

        if self._status:
            if self._owner == threading.current_thread().name:
                if self._as_list:
                    self._as_list = False
                else:
                    self._as_list = True
                return self._as_list
            else:
                raise AccessDeniedError(f"thread {threading.current_thread().name} is not the container owner")
        else:
            if self._as_list:
                self._as_list = False
            else:
                self._as_list = True
            return self._as_list
