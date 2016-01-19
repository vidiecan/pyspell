# coding=utf-8
# See main file for licence
# pylint: disable=
import codecs
import os
import re
import logging

_logger = logging.getLogger("pyspell")

from ._utils import missing_file, invalid_format, line_strip


class dic_mgr(object):
    """

    """

    def __init__(self, file_str, aff):
        self._fs = file_str
        self._d = {}
        self._aff = aff
        self._flag_decoder = self._aff.flag_decoder()

    def parse(self):
        if not os.path.exists(self._fs):
            raise missing_file("aff file missing")

        with codecs.open(self._fs, mode="r+", encoding="utf-8") as fin:
            size = -1
            for l in fin:
                l = line_strip(l)
                if 1 != len(l.split()):
                    # TODO!!! st:|
                    _logger.warn(u"DIC has invalid line, skipping - [%s]" % l)
                    continue
                    #raise invalid_format(".dic in not supported format [%s]" % l)

                # first line
                if -1 == size:
                    size = int(l)
                    continue

                parts = l.split("/")
                # no affix
                if 1 == len(parts):
                    self._d[parts[0]] = [self.entry()]
                    continue
                # affix
                affixes = self._flag_decoder(parts[1])
                if parts[0] not in self._d:
                    self._d[parts[0]] = []
                self._d[parts[0]].append(self.entry(affixes=affixes))

        # we can optimise search by grouping similar prefixes

    @staticmethod
    def entry(affixes=None):
        return {
            "affixes": affixes or (),
        }

    def unmunch_words(self, unique=True):
        for rootword, ds in self._d.iteritems():
            for d in ds:
                if d["affixes"] is None:
                    yield rootword
                else:
                    words = []

                    # get all suffix versions
                    for affix_entry in d["affixes"]:
                        fx = self._aff.get_sfx(affix_entry)
                        if fx is not None:
                            for expanded in self._aff.apply_suffix(rootword, fx):
                                words.append(expanded)

                    # get all suffix + prefix versions
                    for affix_rule in d["affixes"]:
                        fx = self._aff.get_pfx(affix_rule)
                        if fx is not None and fx["combined"]:
                            sz = len(words)
                            for i in range(sz):
                                for expanded in self._aff.apply_prefix(words[i], fx):
                                    words.append(expanded)

                    words.insert(0, rootword)
                    # get all prefix
                    for affix_rule in d["affixes"]:
                        fx = self._aff.get_pfx(affix_rule)
                        if fx is not None:
                            for expanded in self._aff.apply_prefix(rootword, fx):
                                words.append(expanded)

                    if unique:
                        words = set(words)
                    for word in words:
                        yield word

    def __contains__(self, item):
        return item in self._d

    def get(self, item, default=None):
        return self._d.get(item, default)

    def iteritems(self):
        for k, v in self._d.iteritems():
            yield k, v
