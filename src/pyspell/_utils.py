# coding=utf-8

import re


# exceptions
#

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


# text handling
#

def line_strip(line):
    line = line.rstrip( )
    # faster than .rfind()
    if "#" in line:
        pos = line.rfind("#")
        return line[:pos]
    return line


# slovak alphabet
alphabet = u"aáäbcčdďeéfghiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž"
alphabet += alphabet.upper()
valid_chars_re = re.compile(u"^[%s]+$" % alphabet, re.U)


def non_sk_words(w):
    if valid_chars_re.match(w) is None:
        return True
    return False


def trie_like_set(d, key, value):
    """ Trie like insert. """
    if 0 == len(key):
        d.setdefault("", []).append(value)
    else:
        v = d.setdefault(key[0], {})
        trie_like_set(v, key[1:], value)


def trie_like_get(d, key, ret):
    """ Trie like search - because of performance. """
    if 0 != len(key):
        if "" in d:
            ret += d[""]
        if key[0] in d:
            trie_like_get(d[key[0]], key[1:], ret)
