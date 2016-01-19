# -*- coding: utf-8 -*-
# author: jm
import sys

import test


class test_parsing( test.test_case ):

    def test_aff_parsing( self ):
        """ test_aff_parsing """
        from pyspell.aff import aff_mgr
        aff = aff_mgr(self.aff_file())
        aff.parse()
        print aff

    def test_dic_parsing( self ):
        """ test_dic_parsing """
        from pyspell.dic import dic_mgr
        dic = dic_mgr(self.dic_file(), lambda x: x)
        dic.parse()

    def test_inspect( self ):
        """ test_inspect """
        from pyspell import speller
        s = speller(self.aff_file(), self.dic_file())
        s.init()
        s.inspect(lambda x: self.log(x))

    def test_unmunch( self ):
        """ test_unmunch """
        from pyspell.dic import dic_mgr
        from pyspell.aff import aff_mgr

        aff = aff_mgr(self.aff_file("mini"))
        aff.parse()

        dic = dic_mgr(self.dic_file("mini"), aff)
        dic.parse()
        i = 0
        s = set()
        for w in dic.unmunch_words(False):
            #self.assertNotIn(w, s)
            s.add(w)
            i += 1
            try:
                msg = "%3d: %s" % (i, w.encode("utf-8"))
                self.log(msg)
                #print "%3d: %s" % (i, w.encode("utf-8"))
            except:
                pass
