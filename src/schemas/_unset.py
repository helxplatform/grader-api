""" Pydantic has literally no support for doing partial updates with non-nullable fields.
They probably won't ever add it since they have been ignoring this use case for years (SINCE 2020),
so we have to use UNSET as the default for non-nullable fields to allow non-optional values
to be excluded without throwing away the validation functionality. """

class _UNSET:
    def __bool__(self):
        return False
    def __repr__(self):
        return "UNSET"


UNSET = _UNSET()