from .dispatcher import dispatch

# For use with static events.
def dispatches(*args, **kwargs):
    def inner(func):
        result = func()
        dispatch(*args, **kwargs)
        return result
    return inner