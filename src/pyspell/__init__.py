# coding=utf-8
import logging
from .aff import aff_mgr
from .dic import dic_mgr
_logger = logging.getLogger("pyspell")


class speller(object):
    """

    """

    def __init__(self, aff_file, dic_file):
        self._aff = aff_mgr(aff_file)
        self._dic = dic_mgr(dic_file, self._aff)

    def init(self):
        self._aff.parse()
        self._dic.parse()

    def AffixMgr_suffix_check(self, word, pfx_key=None):
        for sfx_key, sfx_entry in self._aff.sfxs().iteritems():
            for sfx in sfx_entry["rules"]:
                if 0 == len(sfx["replace"]):
                    for newword in self._aff.remove_suffix(word, sfx):
                        if sfx["condition"].search(newword):
                            word_ds = self._dic.get(newword, [])
                            for word_d in word_ds:
                                if sfx_key in word_d["affixes"]:
                                    if pfx_key is None or pfx_key in word_d["affixes"]:
                                        return newword

        for sfx_key, sfx_entry in self._aff.sfxs().iteritems():
            for sfx in sfx_entry["rules"]:
                if 0 != len(sfx["replace"]):
                    for newword in self._aff.remove_suffix(word, sfx):
                        assert len(newword) != 0
                        if sfx["condition"].search(newword):
                            word_ds = self._dic.get(newword, [])
                            for word_d in word_ds:
                                if sfx_key in word_d["affixes"]:
                                    if pfx_key is None or pfx_key in word_d["affixes"]:
                                        return newword

        return None

    def AffixMgr_prefix_check(self, word):
        for pfx_key, pfx_entry in self._aff.pfxs().iteritems():
            for pfx in pfx_entry["rules"]:
                if 0 == len(pfx["replace"]):
                    for newword in self._aff.remove_prefix(word, pfx):
                        word_ds = self._dic.get(newword, [])
                        for word_d in word_ds:
                            if pfx_key in word_d["affixes"]:
                                return newword
                        if pfx_entry["combined"]:
                            accepted_word = self.AffixMgr_suffix_check(newword, pfx_key)
                            if accepted_word is not None:
                                return accepted_word

        #
        for pfx_key, pfx_entry in self._aff.pfxs().iteritems():
            for pfx in pfx_entry["rules"]:
                if 0 != len(pfx["replace"]):
                    if word.startswith(pfx["replace"]):
                        for newword in self._aff.remove_prefix(word, pfx):
                            word_ds = self._dic.get(newword, [])
                            for word_d in word_ds:
                                if pfx_key in word_d["affixes"]:
                                    return newword
        return None

    def check(self, word, ignorecase=False):
        word = self._aff.remove_ignore(word)

        if word in self._dic:
            return word

        accepted_word = self.AffixMgr_prefix_check(word)
        if accepted_word is not None:
            return accepted_word

        accepted_word = self.AffixMgr_suffix_check(word)
        if accepted_word is not None:
            return accepted_word

        if ignorecase:
            if word.islower():
                iword = word[0].upper() + word[1:]
                return self.check(iword, False)
            else:
                iword = word.lower()
                return self.check(iword, False)

        return None

    def inspect(self, outputter=None):
        outputter = outputter or _logger.info
        from collections import defaultdict
        d = defaultdict(int)
        for k, vs in self._dic.iteritems():
            for v in vs:
                if v["affixes"] is None:
                    continue
                for a in v["affixes"]:
                    d[a] += 1
        import operator
        sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
        for k, v in sorted_d:
            outputter(u"%4s: %d" % (unichr(k), v))
        for fx in self._aff.sfxs().keys():
            if fx not in d:
                outputter(u"SFX not used [%s]" % (unichr(fx)))
        for fx in self._aff.pfxs().keys():
            if fx not in d:
                outputter(u"PFX not used [%s]" % (unichr(fx)))
