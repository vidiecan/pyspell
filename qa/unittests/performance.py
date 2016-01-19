# -*- coding: utf-8 -*-
# author: jm
import codecs
import test

from pyspell import speller
from pyspell._utils import line_strip


if __name__ == "__main__":
    aff_file = test.files.aff_file()[0]
    dic_file = test.files.dic_file()[0]

    s = speller( aff_file, dic_file )
    s.init()
    LOOP = 5

    with codecs.open(dic_file, mode="r+", encoding="utf-8") as fin:
        fin.next()
        for i, l in enumerate(fin):
            w = line_strip(l).split("/")[0]
            # errors in dict
            if " " in w:
                continue
            for i in range(LOOP):
                s.check(w)
                s.check(w + "ehmmm")
            if 0 == (i + 1) % 10000:
                print "done [%d]" % i



