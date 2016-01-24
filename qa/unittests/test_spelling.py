# -*- coding: utf-8 -*-
# author: jm
import codecs
import test


class test_spelling( test.test_case ):

    def test_spell_origin( self ):
        """ test_spell_origin """
        from pyspell import speller
        from pyspell._utils import line_strip
        s = speller(
            self.aff_file(),
            self.dic_file(),
        )
        s.init()

        with codecs.open(self.dic_file(), mode="r+", encoding="utf-8") as fin:
            fin.next()
            for i, l in enumerate(fin):
                w = line_strip(l).split("/")[0]
                # errors in dict
                if " " in w:
                    continue
                self.assertTrue(s.check(w))
                self.assertFalse(s.check(w + "ehmmm"))
                if 0 == (i + 1) % 10000:
                    self.log("done [%d]" % i)

    def test_text( self ):
        """ test_text """
        from pyspell import speller
        s = speller(
            self.aff_file("mini"),
            self.dic_file("mini"),
        )
        s.init()

        with codecs.open(self.text_file("mini"), mode="r+", encoding="utf-8") as fin:
            guru_accepted = None
            for l in fin:
                for w in l.split():
                    self.log(u"Testing [%s]" % w)
                    accepted = s.check(w)
                    if guru_accepted is None:
                        guru_accepted = accepted
                    self.assertIsNotNone(accepted)
                    self.log(u"+-accepted [%s]" % accepted)
                    self.assertEqual(accepted, guru_accepted)

    def test_ignorecase_text( self ):
        """ test_ignorecase_text """
        from pyspell import speller
        s = speller(
            self.aff_file("small"),
            self.dic_file("small"),
        )
        s.init()

        for w, flag, expected in (
                (u"Abcházska", True, True),
                (u"abcházska", True, True),
                (u"Abcházsko", True, True),
                (u"abcházsko", True, True),

                ("Bratislava", False, True),
                ("Bratislave", False, True),
                ("Bratislavy", False, True),
                ("bratislava", False, False),
                ("bratislave", False, False),
                ("bratislavy", False, False),
        ):
            self.assertEqual(expected, s.check(w, flag) is not None)

    def test_arbitrary_affix( self ):
        """ test_arbitrary_affix """
        from pyspell import speller
        s = speller(
            self.aff_file("small"),
            self.dic_file("small"),
        )
        s.init()

        for w, flag, expected in (
                ("ammm", False, False),
                ("am", False, False),
        ):
            self.assertEqual(expected, s.check(w, flag) is not None)

    def test_hunspell_compatibility( self ):
        """ test_hunspell_compatibility """
        from pyspell import speller
        s = speller(
            self.aff_file(),
            self.dic_file(),
        )
        s.init()

        bad = set()
        with codecs.open(
            self.file("hunspell_results/wiki-words.txt"),
            mode="r+",
            encoding="utf-8"
        ) as fin_words:
            for word in fin_words:
                word = word.strip()
                accepted = s.check(word)
                if accepted is None:
                    bad.add(word)
        bad_expected = set()
        with codecs.open(
            self.file("hunspell_results/wiki-words.txt.bad.results"),
            mode="r+",
            encoding="utf-8"
        ) as fin_results:
            for word in fin_results:
                bad_expected.add(word.strip())
        diff1 = bad_expected - bad
        print diff1
        self.assertTrue(0 == len(diff1))
        diff2 = bad - bad_expected
        print diff2
        self.assertTrue(0 == len(diff2))
