from os import path
from setuptools import setup, find_packages

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

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
    package_dir={'': 'src'},
    packages=find_packages("src", exclude="example"),
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.5',
    test_suite="tests.tests",
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
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Logging',
    ]
)
