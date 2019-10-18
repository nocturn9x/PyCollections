from errors.exceptions import errors


class ConstantDict:
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
       attribute via {object}_ConstantDict__d.

       This mapping is indeed intended to reduce the probability of ACCIDENTALLY overwriting those
       values, if you are looking for immutable objects natively, just
       switch to Java :)"""

    def __init__(self):
        """Initializes self"""

        self.as_dict = False
        self.__d = dict()  # This attribute MUST NOT BE TOUCHED

    def __dir__(self):
        """Overrides dir(object)"""

        raise errors.AccessDeniedError("Access Denied")

    @property
    def __dict__(self):
        """This method (actually, a property) forbids the user to access
           the '__dict__' property, attribute of any python object

           Overriding the __dict__ attribute with a property
           ensures that the ConstantDict values remain unchanged"""

        raise errors.AccessDeniedError("Access Denied")

    @property
    def __class__(self):
        """This property returns the type of the ConstantDict.

           The class is built so that it can emulate Python dicts,
           see below 'typeof' property for more detailed info"""

        if self.as_dict:
            return type(self.__d)
        else:
            return type(self)

    @property
    def typeof(self):
        """The ConstantDict class is built so that it can emulate
           Python dicts, by manipulating the value returned by the __class__ parameter

           To pass isinstance() check, use ConstantDict.typeof() as first argument,
       otherwise just use ConstantDict.typeof (Notice the absence of parenthesis)"""

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
             raises  ConstantError"""

        raise errors.ConstantError("Operation not permitted")

    def __setitem__(self, key, value):
        """Overrides the standard __setitem__ bound method for dicts,
           disallowing the user to edit already existing values inside the container"""

        if key in self.__d:
            raise errors.ConstantError(f"Cannot overwrite existing key. Value for '{key}' is already '{self.__d[key]}'")
        else:
            self.__d[key] = value

    def __iter__(self):
        return self.__d.__iter__()

    def __getitem__(self, key):
        return self.__d.__getitem__(key)

    def __len__(self):
        return self.__d.__len__()

    def __contains__(self, item):
        return dict.__contains__(self.__d, item)

    def __repr__(self):
        return str(self.__d)


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
        self._indexes = dict()  # The numerical indexes for every item in the tuple are saved with their corresponding keyword
        if kwargs:
            self.formatted_args = "("
            for index, key in enumerate(kwargs):
                if not index + 1 == len(kwargs):
                    if isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                        self.formatted_args += f"{key}={kwargs[key]}, "
                    else:
                        self.formatted_args += f"{key}='{kwargs[key]}', "
                else:
                    if isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                        self.formatted_args += f"{key}={kwargs[key]}"
                    else:
                        self.formatted_args += f"{key}='{kwargs[key]}'"
            self.formatted_args += ")"
            self.create_tuple()
        else:
            self.formatted_args = "()"

    def create_tuple(self):
        """This function memorizes all the required
        information for the container to work properly"""

        args = self.formatted_args.replace(" ", "").replace("(", "").replace("'", "").replace(")", "").split(",")
        for arg in args:
            key, value = arg.split("=")
            if value.isdigit():
                value = int(value)
            elif self.isfloat(value):
                value = self.isfloat(value)
            self._dict[key] = value
        self._container = tuple(item[1] for item in self._dict.items())
        for item in self._dict.items():
            self._indexes[item[0]] = self._container.index(item[1])

    @staticmethod
    def isfloat(value):  #Thanks to https://www.geeksforgeeks.org/python-check-for-float-string/
        if value.replace('.', '', 1).isdigit():
            return float(value)
        else:
            return False

    def __str__(self):
        return self.formatted_args

    def __repr__(self):
        return self.formatted_args

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

    def find(self, item):
        """This function finds an element inside the tuple,
        given the item numerical index or a key"""

        if item in self._indexes:
            return self._indexes[item]
        else:
            raise KeyError("item not in tuple")

    def keys(self):
        """This function returns all the keys inside the tuple"""

        keys = []
        for key in self._dict.keys():
            keys.append(key)
        return keys

    def items(self):
        """This function returns all the values inside the tuple"""

        items = []
        for item in self._dict.items():
            items.append(item[1])
        return items

