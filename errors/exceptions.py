class errors:
   """Exceptions for customcollections module"""

   class ConstantError(TypeError):
      pass

   class AccessDeniedError(AttributeError):
      pass

   class WrongKeyError(TypeError):
      pass
