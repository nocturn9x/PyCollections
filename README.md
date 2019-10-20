# PyCollections
PyCollections is a Python 3 library that implements some useful containers (tuples, dictionaries, lists)


### Note

You can find the package also on [PyPI](https://pypi.org/project/PyCollections/), though that page will be updated only when a bunch of minor fixes are made to this repo, so if you want to have always the latest (development) version of PyCollections you should check this repository, too.

## A bit of information

PyCollections implements some cool containers based on Python's builtins such as lists, tuples, dicts and sets.

These containers, or collections, behave slightly different from their parent class as explained below.

At the time of writing, PyCollections is in Development Status 3 (Alpha) and has reached version 0.2.0, that implements:

  - ConstantDict() -> A dictionary whose key-value couples cannot be overwritten nor deleted once set
  - NamedTuple() -> Behaves exactly like a tuple, but has named arguments and can be accessed with literal indexes like dicts
  - LockedList() -> A list that can be locked or unlocked, allowing or disallowing access to the list itself
  - RLockedList() -> Inspired by threading's RLock() class, this special list cannot be accessed by other threads once acquired (It needs to be released to access it)

### ConstantDict() - Docs

#### Introduction

This class implements a 'constant' (or immutable) mapping, we'll face those apexes in a second.

ConstantDict inherits most of its functions from Python's built-in mapping objects: dicts.
This mapping mostly behaves like an usual python dict, except for  4 things:

  - Once a key-value pair is inserted, it cannot be removed anymore
  - Existing key-value pairs cannot be overwritten
  - Attempting to access the `__dict__` attribute will fail
  - Attempting to access dir(object) will fail

These characteristics have been specifically implemented to avoid item's accidental overwrite/deletion.

Let's face the apexes at the beginning: In pure Python, it's impossible to implement an immutable container as it is duck typed: tuples and frozen sets, for example, are implemented in C AND Python, this allowing them to be truly immutable.

You might be wondering, "Soo, how does this class even exists? Didn't you just say it's impossible?!"

Yeah, it is, and actually this mapping is not truly immutable: it just overwrites any known standard method to access mappings values and edit them, but it is still possible to edit those values by accessing the class attribute via {object}_ConstantDict__container.

This mapping is indeed intended to reduce the probability of ACCIDENTALLY overwriting those
values, if you are looking for immutable objects natively, just
switch to Java :)

### Methods

  - `act_as_dict(self)` -> Bound method to activate/deactivate Python dict emulation. Returns the value of the act_as_dict instance attribute once called
  
  - `@property
    typeof(self)` -> The ConstantDict class is built so that it can emulate Python dicts.
    To pass isinstance() check, use ConstantDict.typeof() as first argument, after having called act_as_dict() on the container
    
    
   
