# coding=utf-8
# See main file for licence
# pylint: disable=
import codecs
import os
import bisect
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
        self._empty_entry = dic_mgr.entry(affixes=())

    def parse(self):
        if not os.path.exists(self._fs):
            raise missing_file("aff file missing")

        with codecs.open(self._fs, mode="r+", encoding="utf-8") as fin:
            size = -1
            for l in fin.readlines():
                l = line_strip(l)
                if -1 != l.find(" "):
                    # TODO!!! st:|
                    _logger.warn(u"DIC has invalid line, skipping - [%s]" % l)
                    continue
                    #raise invalid_format(".dic in not supported format [%s]" % l)

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
                    e = dic_mgr.entry(affixes=affixes)
                    if word not in self._d:
                        self._d[word] = [e]
                    else:
                        self._d[word].append(e)
                else:
                    # no affix
                    self._d[l] = [self._empty_entry]
                    continue

        # we can optimise search by grouping similar prefixes

    @staticmethod
    def entry(affixes):
        return { "affixes": u''.join(sorted(affixes)) }

    def unmunch_words(self, unique=True):
        for rootword, ds in self._d.iteritems():
            for d in ds:
                if 0 == len(d["affixes"]):
                    yield rootword
                else:
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

    def __contains__(self, item):
        return item in self._d

    def get(self, item, default=None):
        return self._d.get(item, default)

    def iteritems(self):
        for k, v in self._d.iteritems():
            yield k, v

    @staticmethod
    def has_affixes(word_ds, affixes):
        for word_d in word_ds:
            found = True
            for aff in affixes:
                if aff is None:
                    continue
                word_affs = word_d["affixes"]
                #if aff not in word_affs:
                i = bisect.bisect_left(word_affs, aff)
                if i == len(word_affs) or word_affs[i] != aff:
                    found = False
                    break
            if found:
                return True
        return False
