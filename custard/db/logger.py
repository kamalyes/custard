# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  logger.py
@Time    :  2020/9/25 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""

import logging
from logging import DEBUG, ERROR, FATAL, INFO, WARN, getLogger

__all__ = ['getLogger', 'INFO', 'WARN', 'DEBUG', 'TRACE', 'ERROR', 'FATAL', 'logger']

TRACE = logging.TRACE = DEBUG - 5
logging.addLevelName(TRACE, 'TRACE')

FORMAT = '%(relativeCreated)d %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = getLogger('dts')


def __add_options(parser):
    levels = ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    parser.add_argument(
        '--log-level',
        choices=levels,
        metavar="LEVEL",
        default='INFO',
        dest='loglevel',
        help='Amount of detail in build-time console messages. LEVEL may be one of %s (default: %%(default)s).' %
             ', '.join(levels),
    )


def __process_options(parser, opts):
    try:
        level = getattr(logging, opts.loglevel.upper())
    except AttributeError:
        parser.error('Unknown log level `%s`' % opts.loglevel)
    else:
        logger.setLevel(level)
