# coding=utf-8
# pylint: disable=W0612,W0613

import codecs
import os
import re
from ._utils import missing_file, not_implemented_yet, deprecated, invalid_format, line_strip, \
    trie_like_set, trie_like_get


def decode_default(x):
    """ Supported decoding. """
    return x
    #return map(ord, x)
    #return [ord(c) for c in x]


# noinspection PyMethodMayBeStatic
class aff_mgr( object ):
    """
        Rules definition with several performance optimisations.

        Only a subset of the functionality is implemented.
        An exception is throws if we detect the usage of an unsupported
        keyword.

        Dictionary should be in UTF-8 encoding.
    """

    def __init__(self, file_str):
        self._fs = file_str
        self._try_string = None
        self._ignore = ""
        self._reps = { }
        self._pfxs = { }
        self._sfxs = { }
        self._sfxs_rules = {}
        self._pfxs_rules = {}
        self._breaks = []
        self._needaffix = None
        self._flagdecoder = decode_default

    def __str__(self):
        return "%s (#pfxs:%d #sfxs:%d)" % (self.__class__, len( self._pfxs ), len( self._sfxs ))

    def flag_decoder(self):
        return self._flagdecoder

    def parse(self):
        if not os.path.exists( self._fs ):
            raise missing_file(".aff file missing [%s]" % self._fs)

        with codecs.open( self._fs, mode="r+", encoding="utf-8" ) as fin:
            for l in fin:
                l = line_strip( l )
                first = l.split( " ", 1 )
                if 2 != len( first ):
                    continue
                meth = "_parse_" + first[0]
                if hasattr( self, meth ):
                    # call parse_*WORD*
                    getattr( self, meth )( first[1], fin )
                else:
                    if 0 == len(first) or 0 == len(first[0]) or first[0][0] == "#":
                        continue
                    # several keywords
                    if first[0].startswith( "COMPOUND" ):
                        raise not_implemented_yet( "I do not know COMPOUND*" )
                    if first[0].startswith( "CHECKCOMPOUND" ):
                        raise not_implemented_yet( "I do not know CHECKCOMPOUND*" )
                    raise not_implemented_yet( "I do not know [%s]" % first[0] )

            # we can optimise search by grouping similar prefixes
            self.pfxs_rules_for_search()
            self.sfxs_rules_for_search()

    def sfxs_rules_for_search(self):
        for sfx_key, sfx_entry in self.sfxs():
            for sfx in sfx_entry["rules"]:
                if 0 == len(sfx["with"]):
                    self._sfxs_rules.setdefault("", []).append(sfx)
                else:
                    trie_like_set(self._sfxs_rules, sfx["with"][::-1], sfx)
        return

    def pfxs_rules_for_search(self):
        for pfx_key, pfx_entry in self.pfxs():
            for pfx in pfx_entry["rules"]:
                if 0 == len(pfx["with"]):
                    self._pfxs_rules.setdefault("", []).append(pfx)
                else:
                    trie_like_set(self._pfxs_rules, pfx["with"], pfx)
        return

    def remove_ignore(self, l):
        if 0 == len( self._ignore ):
            return l
        translation_table = dict.fromkeys( [ord(x) for x in ord, self._ignore], None )
        return l.translate( translation_table )

    def sfxs(self):
        return self._sfxs.iteritems()

    def sfxs_rules(self, word_filter):
        ret = []
        trie_like_get(self._sfxs_rules, word_filter[::-1], ret)
        return ret

    def pfxs(self):
        return self._pfxs.iteritems()

    def pfxs_rules(self, word_filter):
        ret = []
        trie_like_get(self._pfxs_rules, word_filter, ret)
        return ret

    def get_sfx(self, key):
        return self._sfxs.get(key, None)

    def get_pfx(self, key):
        return self._pfxs.get(key, None)

    @staticmethod
    def apply_suffix(word, sfx_entry, fullstrip=1):
        sz = len(word)
        for sfx in sfx_entry["rules"]:
            replace_sz = len(sfx["replace"])
            if sz + fullstrip > replace_sz:
                if 0 == replace_sz or word.endswith(sfx["replace"]):
                    m = sfx["condition"].search(word)
                    if m:
                        if 0 < replace_sz:
                            yield word[:-replace_sz] + sfx["with"]
                        else:
                            yield word + sfx["with"]

    @staticmethod
    def apply_prefix(word, pfx, fullstrip=1):
        sz = len(word)
        replace_sz = len(pfx["replace"])
        if sz + fullstrip > replace_sz:
            if 0 == replace_sz or word.startswith(pfx["replace"]):
                m = pfx["condition"].search(word)
                if m:
                    if 0 < replace_sz:
                        yield pfx["with"] + word[replace_sz:]
                    else:
                        yield pfx["with"] + word

    @staticmethod
    def remove_prefix(word, pfx, fullstrip=1):
        with_sz = len(pfx["with"])
        if len(word) + fullstrip > with_sz:
            if 0 == with_sz or word[:with_sz] == pfx["with"]:
                if 0 == len(pfx["replace"]):
                    return word[with_sz:]
                else:
                    return pfx["replace"] + word[with_sz:]
        return None

    @staticmethod
    def remove_suffix(word, sfx, fullstrip=1):
        with_sz = len(sfx["with"])
        if len(word) + fullstrip > with_sz:
            if 0 == with_sz:
                return word + sfx["replace"]
            elif word[-with_sz:] == sfx["with"]:
                return word[:-with_sz] + sfx["replace"]
        return None

    # ======================
    # implemented flags
    #

    def _parse_SET(self, line, *args):
        if line != "UTF-8":
            raise not_implemented_yet( "valid for SET UTF-8 only" )

    def _parse_TRY(self, line, *args):
        self._try_string = line

    def _parse_REP(self, line, *args):
        """
            REP number_of_replacement_definitions

           REP what replacement
                  We  can  define  language-dependent  phonetic information in the
                  affix file (.aff)  by a replacement table.   First  REP  is  the
                  header of this table and one or more REP data line are following
                  it. With this table, Hunspell can suggest the  right  forms  for
                  the  typical  faults of spelling when the incorrect form differs
                  by more, than 1 letter from  the  right  form.   For  example  a
                  possible   English   replacement   table  definition  to  handle
                  misspelled consonants:

                  REP 8
                  REP f ph
                  REP ph f
                  REP f gh
                  REP gh f
                  REP j dg
                  REP dg j
                  REP k ch
                  REP ch k

           Note I: It’s very useful to define replacements for  the  most  typical
           one-character  mistakes, too: with REP you can add higher priority to a
           subset of the TRY suggestions (suggestion  list  begins  with  the  REP
           suggestions).

           Note  II:  Suggesting  separated  words by REP, you can specify a space
           with an underline:

                  REP 1
                  REP alot a_lot

           Note III: Replacement table can be used for a  stricter  compound  word
           checking  (forbidding generated compound words, if they are also simple
           words with typical fault, see CHECKCOMPOUNDREP).
        """
        parts = line.split( )

        # the first REP - should be int
        if 1 == len( parts ):
            try:
                int( parts[0] )
                return
            except:
                raise invalid_format( "AFF invalid REP [%s]" % line )
        elif 2 != len( parts ):
            raise invalid_format( "AFF invalid REP [%s]" % line )

        # other REPs
        if parts[0][0] == "^":
            raise not_implemented_yet( "REP ^ in pattern" )
        if parts[0][-1] == "$":
            raise not_implemented_yet( "REP $ in pattern" )
        # store REPs
        self._reps[parts[0]] = parts[1].replace( "_", " " )

    def parse_FX(self, line, fin, d, condition_re, tag):
        # split now
        parts = line.split( )
        # we assume it is one character
        if 1 != len( parts[0] ):
            raise not_implemented_yet( "%s in unexpected format [%s]" % (tag, line) )
        aflag = parts[0]
        if aflag in d:
            raise invalid_format( "%s has invalid format [%s] - rule already defined" % (tag, line) )
        #
        crossproduct = ("Y" == parts[1])
        pos = 2 if crossproduct else 1

        if aflag not in d:
            d[aflag] = {
                "rules": [],
                "combined": crossproduct  # can be combined with prefixes/suffixes
            }

        line_nums = int( parts[pos] )
        for i in range( line_nums ):
            # ?FX FLAG TOSTRIP_OR_0 AFFIX_OR_0
            l = line_strip( fin.next( ) )
            parts = l.split( )
            if 5 > len( parts ):
                raise invalid_format( "%s invalid format [%s]" % (tag, l) )
            # must match FLAG from the first line
            aflag_tmp = parts[1]
            if aflag != aflag_tmp:
                raise invalid_format( "%s invalid format [%s] - FLAGS do not match" % (tag, l) )

            replace = parts[2] if "0" != parts[2] else ""
            wwith = parts[3] if "0" != parts[3] else ""

            affix_flag_part = None
            if "/" in wwith:
                slash_in_affix = wwith.rfind( "/" )
                affix_flag_part = wwith[slash_in_affix + 1:]
                wwith = wwith[:slash_in_affix]
            condition = parts[4]

            if aflag not in d:
                d[aflag] = []

            replace = self.remove_ignore(replace)

            # see affentry.cxx at the end of the file
            fx = {
                "aflag": aflag,
                "replace": replace,
                "with": wwith,
                "append_flag": affix_flag_part,
                "condition": re.compile( condition_re % condition, re.U ),
            }
            if not crossproduct:
                fx["not_combine"] = True
            d[aflag]["rules"].append(fx)

    def _parse_PFX(self, line, fin, *args):
        self.parse_FX( line, fin, self._pfxs, "^%s", "PFX" )

    def _parse_SFX(self, line, fin, *args):
        self.parse_FX( line, fin, self._sfxs, "%s$", "SFX"  )

    def _parse_IGNORE(self, line, *args):
        self._ignore = line

    def _parse_BREAK(self, line, fin, *args):
        parts = line.split( )
        line_nums = int( parts[0] )
        for i in range( line_nums ):
            l = line_strip( fin.next( ) )
            parts = l.split( )
            self._breaks.append( parts[0] )

    def _parse_NEEDAFFIX(self, line, *args):
        self._needaffix = line

    # ======================
    # should implement
    #

    def _parse_CIRCUMFIX(self, line, *args):
        raise not_implemented_yet( "I do not know CIRCUMFIX" )

    def _parse_KEY(self, line, *args):
        """
            KEY characters_separated_by_vertical_line_optionally
                  Hunspell  searches  and  suggests  words  with   one   different
                  character  replaced  by  a  neighbor KEY character. Not neighbor
                  characters in KEY string separated by vertical line  characters.
                  Suggested KEY parameters for QWERTY and Dvorak keyboard layouts:

                  KEY qwertyuiop|asdfghjkl|zxcvbnm
                  KEY pyfgcrl|aeouidhtns|qjkxbmwvz

           Using the first QWERTY layout, Hunspell suggests "nude" and "node"  for
           "*nide". A character may have more neighbors, too:

                  KEY qwertzuop|yxcvbnm|qaw|say|wse|dsx|sy|edr|fdc|dx|rft|gfv|fc|tgz|hgb|gv|zhu|jhn|hb|uji|kjm|jn|iko|lkm
        """
        raise not_implemented_yet( "I do not know KEY" )

    def _parse_PHONE(self, line, *args):
        raise not_implemented_yet( "I do not know PHONE" )

    def _parse_MAP(self, line, *args):
        raise not_implemented_yet( "I do not know MAP" )

    def _parse_VERSION(self, line, *args):
        raise not_implemented_yet( "I do not know VERSION" )

    def _parse_SUBSTANDARD(self, line, *args):
        raise not_implemented_yet( "I do not know SUBSTANDARD" )

    # ======================
    # not implemented yet
    #

    def _parse_FORBIDDENWORD(self, line, *args):
        raise not_implemented_yet( "I do not know FORBIDDENWORD" )

    def _parse_FLAG(self, line, *args):
        raise not_implemented_yet( "I do not know FLAG" )

    def _parse_LANG(self, line, *args):
        raise not_implemented_yet( "I do not know LANG" )

    def _parse_AF(self, line, *args):
        raise not_implemented_yet( "I do not know AF" )

    def _parse_AM(self, line, *args):
        raise not_implemented_yet( "I do not know AM" )

    def _parse_COMPLEXPREFIXES(self, line, *args):
        raise not_implemented_yet( "I do not know COMPLEXPREFIXES" )

    def _parse_SIMPLIFIEDTRIPLE(self, line, *args):
        raise not_implemented_yet( "I do not know SIMPLIFIEDTRIPLE" )

    def _parse_NOSUGGEST(self, line, *args):
        raise not_implemented_yet( "I do not know NOSUGGEST" )

    def _parse_NONGRAMSUGGEST(self, line, *args):
        raise not_implemented_yet( "I do not know NONGRAMSUGGEST" )

    def _parse_ONLYINCOMPOUND(self, line, *args):
        raise not_implemented_yet( "I do not know ONLYINCOMPOUND" )

    def _parse_SYLLABLENUM(self, line, *args):
        raise not_implemented_yet( "I do not know SYLLABLENUM" )

    def _parse_CHECKNUM(self, line, *args):
        raise not_implemented_yet( "I do not know CHECKNUM" )

    def _parse_WORDCHARS(self, line, *args):
        raise not_implemented_yet( "I do not know WORDCHARS" )

    def _parse_ICONV(self, line, *args):
        raise not_implemented_yet( "I do not know ICONV" )

    def _parse_OCONV(self, line, *args):
        raise not_implemented_yet( "I do not know OCONV" )

    def _parse_CHECKCOMPOUNDPATTERN(self, line, *args):
        raise not_implemented_yet( "I do not know CHECKCOMPOUNDPATTERN" )

    def _parse_MAXNGRAMSUGS(self, line, *args):
        raise not_implemented_yet( "I do not know MAXNGRAMSUGS" )

    def _parse_ONLYMAXDIFF(self, line, *args):
        raise not_implemented_yet( "I do not know ONLYMAXDIFF" )

    def _parse_MAXDIFF(self, line, *args):
        raise not_implemented_yet( "I do not know MAXDIFF" )

    def _parse_MAXCPDSUGS(self, line, *args):
        raise not_implemented_yet( "I do not know MAXCPDSUGS" )

    def _parse_NOSPLITSUGS(self, line, *args):
        raise not_implemented_yet( "I do not know NOSPLITSUGS" )

    def _parse_XXX(self, line, *args):
        raise not_implemented_yet( "I do not know xxx" )

    def _parse_FULLSTRIP(self, line, *args):
        raise not_implemented_yet( "I do not know FULLSTRIP" )

    def _parse_SUGSWITHDOTS(self, line, *args):
        raise not_implemented_yet( "I do not know SUGSWITHDOTS" )

    def _parse_KEEPCASE(self, line, *args):
        raise not_implemented_yet( "I do not know KEEPCASE" )

    def _parse_FORCEUCASE(self, line, *args):
        raise not_implemented_yet( "I do not know FORCEUCASE" )

    def _parse_WARN(self, line, *args):
        raise not_implemented_yet( "I do not know WARN" )

    def _parse_FORBIDWARN(self, line, *args):
        raise not_implemented_yet( "I do not know FORBIDWARN" )

    def _parse_CHECKSHARPS(self, line, *args):
        raise not_implemented_yet( "I do not know CHECKSHARPS" )

    # ======================
    # deprecated
    #

    def _parse_LEMMA_PRESENT(self, line, *args):
        raise deprecated( "LEMMA_PRESENT" )

    def _parse_PSEUDOROOT(self, line, *args):
        raise deprecated( "PSEUDOROOT" )
