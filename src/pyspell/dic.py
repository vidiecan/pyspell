# coding=utf-8

import codecs
import os
import bisect
import logging
from ._utils import missing_file, line_strip

_logger = logging.getLogger("pyspell")


class dic_mgr(object):
    """
        Simple word -> list of rules abstraction that uses
        binary search for rules.
    """

    def __init__(self, file_str, aff):
        self._fs = file_str
        self._d = {}
        self._aff = aff
        self._flag_decoder = self._aff.flag_decoder()
        self._empty_entry = dic_mgr._entry(affixes=())

    # dict like
    #

    def __contains__(self, item):
        return item in self._d

    def get(self, item, default=None):
        return self._d.get(item, default)

    def iteritems(self):
        for k, v in self._d.iteritems():
            yield k, v

    # api
    #

    def parse(self):
        """
            Parse the dictionary file.

            Will throw if not supported features are detected.
        """
        if not os.path.exists(self._fs):
            raise missing_file(".dic file is missing [%s]" % self._fs)

        with codecs.open(self._fs, mode="r+", encoding="utf-8") as fin:
            size = -1
            for l in fin.readlines():
                l = line_strip(l)
                if " " in l:
                    # TODO!!! st:|
                    _logger.warn(u".dic contains invalid (or unsupported) line, skipping - [%s]", l)
                    continue

                # first line
                if -1 == size:
                    size = int(l)
                    continue

                # .rfind seems the same
                pos = l.find(u"/")
                if -1 != pos:
                    word = l[:pos]
                    flags = l[pos + 1:]
                    # affix
                    affixes = self._flag_decoder(flags)
                    e = dic_mgr._entry(affixes=affixes)
                    self._d.setdefault(word, []).append(e)
                else:
                    # no affix
                    self._d[l] = [self._empty_entry]
                    continue

    @staticmethod
    def has_affixes(word_ds, affixes):
        for word_d in word_ds:
            found = True
            for aff in affixes:
                if aff is None:
                    continue
                word_affs = word_d["affixes"]
                i = bisect.bisect_left(word_affs, aff)
                if i == len(word_affs) or word_affs[i] != aff:
                    found = False
                    break
            if found:
                return True
        return False

    def unmunch_words(self, unique=True):
        """
            Get the list of all files that can be generated.
        """
        for rootword, ds in self._d.iteritems():
            for d in ds:
                if 0 == len(d["affixes"]):
                    yield rootword
                    continue
                words = []

                # get all suffix versions
                for affix_entry in d["affixes"]:
                    fx_entry = self._aff.get_sfx(affix_entry)
                    if fx_entry is None:
                        continue
                    for expanded in self._aff.apply_suffix(rootword, fx_entry):
                        words.append(expanded)

                # get all suffix + prefix versions
                for affix_rule in d["affixes"]:
                    fx_entry = self._aff.get_pfx(affix_rule)
                    if fx_entry is None:
                        continue
                    if fx_entry is not None and fx_entry["combined"]:
                        sz = len(words)
                        for i in range(sz):
                            for fx in fx_entry["rules"]:
                                for expanded in self._aff.apply_prefix(words[i], fx):
                                    words.append(expanded)

                words.insert(0, rootword)
                # get all prefix
                for affix_rule in d["affixes"]:
                    fx_entry = self._aff.get_pfx(affix_rule)
                    if fx_entry is None:
                        continue
                    for fx in fx_entry["rules"]:
                        for expanded in self._aff.apply_prefix(rootword, fx):
                            words.append(expanded)

                if unique:
                    words = set(words)
                for word in words:
                    yield word

    # helpers
    #

    @staticmethod
    def _entry(affixes):
        return { "affixes": u''.join(sorted(affixes)) }
