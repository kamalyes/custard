import abc
import os
import pathlib

if os.name == 'nt':
    # noinspection PyPep8,PyPep8
    import win32con
    import win32file
    import pywintypes

    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    LOCK_SH = 0  # The default value
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    _overlapped = pywintypes.OVERLAPPED()  # noqa
else:
    import fcntl


class BaseLock(metaclass=abc.ABCMeta):
    def __init__(self, lock_file_path: str):
        self.f = open(lock_file_path, 'a')

    @abc.abstractmethod
    def __enter__(self):
        raise NotImplemented

    @abc.abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplemented


class WinFileLock(BaseLock):
    """
    已近经过测试，即使某个脚本把文件锁获得后，突然把那个脚本关了，另一个脚本也会获得文件锁。不会死锁导致代码无限等待。
    """

    def __enter__(self):
        self.hfile = win32file._get_osfhandle(self.f.fileno())  # noqa
        win32file.LockFileEx(self.hfile, LOCK_EX, 0, 0xffff0000, _overlapped)

    def __exit__(self, exc_type, exc_val, exc_tb):
        win32file.UnlockFileEx(self.hfile, 0, 0xffff0000, _overlapped)


class LinuxFileLock(BaseLock):
    def __enter__(self):
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.f, fcntl.LOCK_UN)


FileLock = WinFileLock if os.name == 'nt' else LinuxFileLock

if __name__ == '__main__':
    import time

    print('wait for lock')
    with FileLock(pathlib.Path(__file__).parent / pathlib.Path('test.lock')):
        print('hi')
        time.sleep(1)
        print('hello')
