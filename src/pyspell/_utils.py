# coding=utf-8
# See main file for licence
# pylint: disable=
import re


def line_strip(line):
    line = line.strip( )
    parts = line.split( "#", 1 )
    if 3 > len( parts ):
        return parts[0]
    return line


class missing_file(Exception):

    def __init__(self, message):
        super(missing_file, self).__init__(message)


class not_implemented_yet(Exception):

    def __init__(self, message):
        super(not_implemented_yet, self).__init__(message)


class deprecated(Exception):

    def __init__(self, message):
        super(deprecated, self).__init__(message)


class invalid_format(Exception):

    def __init__(self, message):
        super(invalid_format, self).__init__(message)


alphabet = u"aáäbcčdďeéfghiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž"
alphabet += alphabet.upper()
valid_chars_re = re.compile(u"^[%s]+$" % alphabet, re.U)


def non_sk_words(w):
    if valid_chars_re.match(w) is None:
        return True
    return False

