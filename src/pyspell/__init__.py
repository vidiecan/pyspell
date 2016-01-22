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
        for sfx in self._aff.sfxs_rules(word):
            newword = aff_mgr.remove_suffix(word, sfx)
            if newword is None:
                continue
            if sfx["condition"].search(newword):
                word_ds = self._dic.get(newword, None)
                if word_ds is None:
                    continue
                if dic_mgr.has_affixes(word_ds, (sfx["aflag"], pfx_key)):
                    return newword
        return None

    def AffixMgr_prefix_check(self, word):
        for pfx in self._aff.pfxs_rules(word):
            repl_sz = len(pfx["replace"])
            if 0 != repl_sz and word[:repl_sz] == pfx["replace"]:
                continue
            newword = aff_mgr.remove_prefix(word, pfx)
            if newword is None:
                continue
            if pfx["condition"].search(newword):
                word_ds = self._dic.get(newword, None)
                if word_ds is not None:
                    if dic_mgr.has_affixes(word_ds, (pfx["aflag"],)):
                        return newword
                if "not_combine" in pfx:
                    continue
                accepted_word = self.AffixMgr_suffix_check(newword, pfx["aflag"])
                if accepted_word is not None:
                    return accepted_word
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
            outputter(u"%4s: %d" % (k, v))
        for fx_key, fx_entry in self._aff.sfxs():
            if fx_key not in d:
                outputter(u"SFX not used [%s]" % fx_key)
            else:
                for fx in fx_entry["rules"]:
                    if len(fx["replace"]) > 0:
                        p = fx["condition"].pattern
                        if p[-1] == u"$":
                            p = p[:-1]
                        else:
                            continue
                        if fx["replace"][-1] != p[-1]:
                            outputter(
                                    u"invalid SFX replace [%s] - does not match condition [%s]" % (
                                        fx["replace"], fx["condition"].pattern
                                    )
                            )
        for fx_key, fx_entry in self._aff.pfxs():
            if fx_key not in d:
                outputter(u"PFX not used [%s]" % fx_key)
            else:
                for fx in fx_entry["rules"]:
                    if len(fx["replace"]) > 0:
                        p = fx["condition"].pattern
                        if fx["replace"][0] != p[0]:
                            outputter(
                                    u"invalid PFX replace [%s] - does not match condition [%s]" % (
                                        fx["replace"], fx["condition"].pattern
                                    )
                            )
