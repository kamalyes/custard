import copy
import sys
import time
import types
from functools import wraps

from .exceptions import FunctionTimedOut
from .stop_pable_thread import StoppableThread

__all__ = ('func_timeout', 'func_set_timeout')


def func_timeout(timeout, func, args=(), kwargs=None):
    """
    Args:
        timeout:
        func:
        args:
        kwargs:
    Returns:
    """
    if not kwargs:
        kwargs = {}
    if not args:
        args = ()

    ret = []
    exception = []
    is_stopped = False

    def funcwrap(args2, kwargs2):
        try:
            ret.append(func(*args2, **kwargs2))
        except FunctionTimedOut:
            pass
        except Exception as e:
            exc_info = sys.exc_info()
            if is_stopped is False:
                e.__traceback__ = exc_info[2].tb_next
                exception.append(e)

    thread = StoppableThread(target=funcwrap, args=(args, kwargs))
    thread.daemon = True

    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        is_stopped = True

        class FunctionTimedOutTempType(FunctionTimedOut):
            def __init__(self):
                return FunctionTimedOut.__init__(self, '', timeout, func, args, kwargs)

        stop_exception = type(
            'FunctionTimedOut' + str(hash("%d_%d_%d_%d" % (id(timeout), id(func), id(args), id(kwargs)))),
            FunctionTimedOutTempType.__bases__, dict(FunctionTimedOutTempType.__dict__))
        thread.stop_thread(stop_exception)
        thread.join(min(.1, timeout / 50.0))
        raise FunctionTimedOut('', timeout, func, args, kwargs)
    else:
        thread.join(.5)

    if exception:
        raise exception[0] from None

    if ret:
        return ret[0]


def func_set_timeout(timeout, allow_override=False):
    """
    Args:
        timeout:
        allow_override:
    Returns:
    """
    default_timeout = copy.copy(timeout)

    is_timeout_function = bool(issubclass(timeout.__class__, (
        types.FunctionType, types.MethodType, types.LambdaType, types.BuiltinFunctionType, types.BuiltinMethodType)))

    if not is_timeout_function:
        if not issubclass(timeout.__class__, (float, int)):
            try:
                timeout = float(timeout)
            except ValueError as e:
                raise ValueError(' Passed type: < %s > is not of any of these, and cannot be converted to a float.'
                                 % (timeout.__class__.__name__,))

    if not allow_override and not is_timeout_function:
        def _function_decorator(func):
            return wraps(func)(lambda *args, **kwargs: func_timeout(default_timeout, func, args=args, kwargs=kwargs))

        return _function_decorator

    if not is_timeout_function:
        def _function_decorator(func):
            def _function_wrapper(*args, **kwargs):
                if 'force_timeout' in kwargs:
                    use_timeout = kwargs.pop('force_timeout')
                else:
                    use_timeout = default_timeout

                return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

            return wraps(func)(_function_wrapper)

        return _function_decorator

    timeout_function = timeout

    if allow_override:
        def _function_decorator(func):
            def _function_wrapper(*args, **kwargs):
                if 'force_timeout' in kwargs:
                    use_timeout = kwargs.pop('force_timeout')
                else:
                    use_timeout = timeout_function(*args, **kwargs)

                return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

            return wraps(func)(_function_wrapper)

        return _function_decorator

    def _function_decorator(func):
        def _function_wrapper(*args, **kwargs):
            use_timeout = timeout_function(*args, **kwargs)

            return func_timeout(use_timeout, func, args=args, kwargs=kwargs)

        return wraps(func)(_function_wrapper)

    return _function_decorator


if __name__ == '__main__':
    @func_set_timeout(5)
    def testcase():
        time.sleep(5)
    testcase()
