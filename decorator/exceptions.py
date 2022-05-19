__all__ = ('FunctionTimedOut', 'RETRY_SAME_TIMEOUT')

RETRY_SAME_TIMEOUT = 'RETRY_SAME_TIMEOUT'


class FunctionTimedOut(BaseException):

    def __init__(self, msg='', timed_out_after=None, timed_out_function=None,
                 timed_out_args=None, timed_out_kwargs=None):
        """
        Args:
            msg:
            timed_out_after:
            timed_out_function:
            timed_out_args:
            timed_out_kwargs:
        """
        self.timed_out_after = timed_out_after
        self.timed_out_function = timed_out_function
        self.timed_out_args = timed_out_args
        self.timed_out_kwargs = timed_out_kwargs

        if not msg:
            msg = self.get_msg()

        BaseException.__init__(self, msg)

        self.msg = msg

    def get_msg(self):
        if self.timed_out_function is not None:
            timed_out_func_name = self.timed_out_function.__name__
        else:
            timed_out_func_name = 'Unknown Function'
        if self.timed_out_after is not None:
            timed_out_after_str = "%f" % (self.timed_out_after,)
        else:
            timed_out_after_str = "Unknown"

        return 'Function %s (args=%s) (kwargs=%s) timed out after %s seconds.\n' % (
            timed_out_func_name, repr(self.timed_out_args), repr(self.timed_out_kwargs), timed_out_after_str)

    def retry(self, timeout=RETRY_SAME_TIMEOUT):
        """
        Args:
            timeout:
        Returns:
        """
        if timeout is None:
            return self.timed_out_function(*self.timed_out_args, **self.timed_out_kwargs)

        from .dafunc import func_timeout

        if timeout == RETRY_SAME_TIMEOUT:
            timeout = self.timed_out_after

        return func_timeout(timeout, self.timed_out_function, args=self.timed_out_args, kwargs=self.timed_out_kwargs)
