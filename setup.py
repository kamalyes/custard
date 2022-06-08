import sys
from os import path
from typing import Any

import pytest
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.dist import Distribution

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 7)

if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write(
        """
==========================
Unsupported Python version
==========================
This version of Requests requires at least Python {}.{}, but
you're trying to install it on Python {}.{}. To resolve this,
consider upgrading to a supported Python version.
""".format(
            *(REQUIRED_PYTHON + CURRENT_PYTHON)
        )
    )
    sys.exit(1)

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as file:
    requires = file.readlines()

test_requirements = [
    "pytest-httpbin==0.0.7",
    "pytest-cov",
    "pytest-mock",
    "pytest-xdist",
    "PySocks>=1.5.6, !=1.5.7",
    "pytest>=3",
]


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass into py.test")]

    def __init__(self, dist: Distribution, **kw: Any):
        super().__init__(dist, kw)
        self.test_args = None
        self.pytest_args = None

    def initialize_options(self):
        TestCommand.initialize_options(self)
        try:
            from multiprocessing import cpu_count

            self.pytest_args = ["-n", str(cpu_count()), "--boxed"]
        except (ImportError, NotImplementedError):
            self.pytest_args = ["-n", "1", "--boxed"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="hutools",
    version="1.0.0",
    url="https://github.com/kamalyes/hutools",
    license="BSD",
    include_package_data=True,
    description="A python library adding hutools",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Kamalyes",
    author_email="mryu168@163.com",
    packages=find_packages(exclude="example"),
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.5',
    test_suite="tests.tests",
    install_requires=requires,
    cmdclass={"test": PyTest},
    tests_require=test_requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: System :: Logging',
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
    ]
)
