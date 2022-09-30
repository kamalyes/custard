# -*- coding:utf-8 -*-
# !/usr/bin/env python 3.9.11
"""
@File    :  string.py
@Time    :  2022/9/30 6:55 PM
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
import re

import arrays as _
import utilities as helpers


def camel_case(string=''):
    """Converts string to camel case

    Keyword Arguments:
        string {str} -- The string to convert (default: {''})

    Returns:
        (string) -- Returns the camel cased string
    """
    items = replace_special_characters(string)

    # format first letter for word
    result = [item.lower() if index == 0 else item[0].upper() + item[1:].lower() for index, item in
              enumerate(items)]

    return ''.join(result)


def replace_special_characters(string=''):
    """Replace all special characters of string

    Keyword Arguments:
        string {str} -- The string to replacement (default: {''})

    Returns:
        (list) -- Returns a list string
    """

    # remove all special characters base on pattern
    items = re.split('[-_*)( %^$#@!]', str(string))

    # remove all elements is empty, None, False
    return _.compact(items)


def capitalize(string=''):
    """Converts the first character of string to upper case and the remaining to lower case

    Keyword Arguments:
        string {str} -- The string to capitalize (default: {''})

    Returns:
        (string) -- Returns the capitalized string
    """

    format_string = str(string)
    return format_string[0].upper() + format_string[1:].lower()


def ends_with(string='', target=None, position=None):
    """Checks if string ends with the given target string

    Keyword Arguments:
        string {str} -- The string to inspect (default: {''})
        target {[type]} -- The string to search for (default: {None})
        position {[type]} -- The position to search up to (default: {None})

    Returns:
        (boolean) -- Returns true if string ends with target, else false
    """
    format_string = str(string)
    if position is None or helpers.is_number(position) is not True:
        position = len(format_string)

    return format_string[position - 1] == target


def string_replace(string, old_character, new_character):
    """Replace string with new characters

    Arguments:
        string {string} -- The string to replace
        old_character {string} -- Old character need to replace
        new_character {string} -- New character to replace

    Returns:
        (string) -- Returns the string with new character
    """

    if old_character in str(string):
        string = string.replace(old_character, new_character)

    return string


def escape(string=''):
    """Converts the characters "&", "<", ">", '"', and "'" in string to their corresponding HTML entities

    Keyword Arguments:
        string {str} -- The string to escape (default: {''})

    Returns:
        (string) -- Returns the escaped string
    """
    characters = {
        '&': '&amp;',
        '>': '&gt;',
        '"': '&quot;',
        '\'': '&apos;',
        '<': '&lt;'
    }

    for key, value in characters.items():
        string = string_replace(str(string), key, value)

    return string


def lower_case(string=''):
    """Converts string, as space separated words, to lower case

    Keyword Arguments:
        string {str} -- The string to convert (default: {''})

    Returns:
        string -- Returns the lower cased string
    """

    items = replace_special_characters(string)
    result = [i.lower() for i in items]

    return ' '.join(result)


def lower_first(string=''):
    """Converts the first character of string to lower case

    Keyword Arguments:
        string {str} -- The string to convert (default: {''})

    Returns:
        (string) -- Returns the converted string
    """

    format_string = str(string)
    return format_string[0].lower() + format_string[1:]


def pad_characters(chars, position):
    """Split string with position

    Arguments:
        chars {string} -- The string to split
        position {number} -- Position of string to split

    Returns:
        (string) -- Returns substring
    """

    return (chars * position)[0:position]


def pad(string='', length=0, chars=' '):
    """Pads string on the left and right sides if it's shorter than length. Padding characters are truncated if they can't be evenly divided by length.

    Keyword Arguments:
        string {str} -- The string to pad (default: {''})
        length {int} -- The padding length (default: {0})
        chars {str} -- The string used as padding (default: {' '})

    Returns:
        (string) -- Returns the padded string
    """
    format_string = str(string)
    left = length % len(format_string)
    right = length - len(format_string) - left

    return pad_characters(chars, left) + format_string + pad_characters(chars, right)


def pad_end(string='', length=0, chars=' '):
    """Pads string on the right side if it's shorter than length. Padding characters are truncated if they exceed length

    Keyword Arguments:
        string {str} -- The string to pad (default: {''})
        length {int} -- The padding length (default: {0})
        chars {str} -- The string used as padding (default: {' '})

    Returns:
        (string) -- Returns the padded string
    """
    format_string = str(string)
    right = length - len(format_string)

    return format_string + pad_characters(chars, right)


def pad_start(string='', length=0, chars=' '):
    """Pads string on the left side if it's shorter than length. Padding characters are truncated if they exceed length

    Keyword Arguments:
        string {str} -- The string to pad (default: {''})
        length {int} -- The padding length (default: {0})
        chars {str} -- The string used as padding (default: {' '})

    Returns:
        (string) -- Returns the padded string
    """
    format_string = str(string)
    left = length - len(format_string)

    return pad_characters(chars, left) + format_string


def repeat(string='', n=1):
    """Repeats the given string n times

    Keyword Arguments:
        string {str} -- The string to repeat (default: {''})
        n {int} -- The number of times to repeat the string (default: {1})

    Returns:
        (string) -- Returns the repeated string
    """
    return str(string) * n


def replace(string, pattern, replacement):
    """Replaces matches for pattern in string with replacement

    Arguments:
        string {string} -- The string to modify
        pattern {RegExp|string} -- The pattern to replace
        replacement {Function|string)} -- The match replacement

    Returns:
        (string) -- Returns the modified string
    """
    return str(string).replace(pattern, replacement)


def starts_with(string, target, position=0):
    """Checks if string starts with the given target string

    Arguments:
        string {[type]} -- The string to inspect
        target {[type]} -- The string to search for

    Keyword Arguments:
        position {int} -- The position to search from (default: {0})

    Returns:
        (boolean) -- Returns true if string starts with target, else false
    """
    return str(string)[position] == target
