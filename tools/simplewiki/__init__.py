#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import re
import WikiExtractor
WikiExtractor.expand_templates = False


class wiki(object):

    acceptedNamespaces = ['w', 'wiktionary', 'wikt']
    tagRE = re.compile(r'(.*?)<(/?\w+)[^>]*>(?:([^<]*)(<.*?>)?)?')
    #                    1     2               3      4

    def __init__(self, xml_file):
        self._f = xml_file
        self._templateNamespace = ''
        self._knownNamespaces = set(['Template'])

    def parse_siteinfo(self, iter):
        while True:
            line = iter().strip()
            m = self.tagRE.search(line)
            if not m:
                continue
            tag = m.group(2)
            if tag == 'base':
                # discover urlbase from the xml dump file
                # /mediawiki/siteinfo/base
                base = m.group(3)
                self._urlbase = base[:base.rfind("/")]
            elif tag == 'namespace':
                self._knownNamespaces.add(m.group(3))
                if re.search('key="10"', line):
                    self._templateNamespace = m.group(3)
            elif tag == '/siteinfo':
                break

    def parse_page(self, iter):
        page = []
        id = None
        last_id = None
        ordinal = 0  # page count
        inText = False
        redirect = False
        while True:
            line = iter().strip()
            if '<' not in line:  # faster than doing re.search()
                if inText:
                    page.append(line)
                continue
            m = self.tagRE.search(line)
            if not m:
                continue
            tag = m.group(2)
            if tag == 'page':
                page = []
                redirect = False
            elif tag == 'id' and not id:
                id = m.group(3)
            elif tag == 'title':
                title = m.group(3)
            elif tag == 'redirect':
                redirect = True
            elif tag == 'text':
                inText = True
                line = line[m.start(3):m.end(3)]
                page.append(line)
                if m.lastindex == 4:  # open-close
                    inText = False
            elif tag == '/text':
                if m.group(1):
                    page.append(m.group(1))
                inText = False
            elif inText:
                page.append(line)
            elif tag == '/page':
                colon = title.find(':')
                if (colon < 0 or title[:colon] in self.acceptedNamespaces) and id != last_id and \
                        not redirect and not title.startswith(self._templateNamespace):
                    yield id, title, page, ordinal
                    last_id = id
                    ordinal += 1
                id = None
                page = []

    def pages(self):
        with codecs.open(self._f, mode="r+", encoding="utf-8") as fin:
            self.parse_siteinfo(fin.next)
            for id, title, page, ordinal in self.parse_page(fin.next):
                yield id, title, page

    def words(self, normalise=False, strict_words=True, lowercase=False):

        #? ! . ?" !" ." ?'' !'' .''
        sentence_end_re = re.compile(u"(?:\.|\?|!|\.''|\?''|!''|\?\"|!\"|\.\")$", re.U)

        class outter(object):
            def __init__(self):
                self.ls = []
            def write(self, l):
                self.ls.append(l)
            def text(self):
                return u"".join(self.ls[1:-1])

        pages = 0
        for i, (id, title, page) in enumerate(self.pages()):
            pages += 1
            out = outter()
            WikiExtractor.Extractor(id, title, page).extract(out)
            lastw = None
            for w in out.text().split():
                wnorm = w

                # special case ==Zdroje
                if lastw is None or sentence_end_re.search(lastw):
                    sentence_start = True
                else:
                    sentence_start = False
                if not sentence_start:
                    if w.startswith("==") or lastw.endswith("=="):
                        sentence_start = True

                if normalise:
                    wnorm = self.normalise(w, True, False)

                if strict_words:
                    if wnorm.isupper() or wnorm.isnumeric():
                        wnorm = ""
                    else:
                        wnorm1 = self.normalise(wnorm, False, True)
                        if len(wnorm1) != len(wnorm):
                            wnorm = ""
                    if lowercase and 0 < len(wnorm):
                        wnorm = wnorm.lower()
                # TODO debug
                # if wnorm in(
                #         u"Má",
                # ):
                #     if sentence_start:
                #         pass
                #     else:
                #         pass
                if 0 == len(wnorm):
                    lastw = w
                    continue
                if not sentence_start and w[0].isupper():
                    pass
                if sentence_start and not w[0].isupper():
                    pass
                yield w, wnorm, sentence_start, pages
                lastw = w

    _normalise_re_apos1 = re.compile(ur"(?u)(\W)[‘’′`']", flags=re.U)
    _normalise_re_apos2 = re.compile(ur"(?u)[‘’`′'](\W)", flags=re.U)
    _normalise_re_apos3 = re.compile(ur'(?u)[«»“”]', flags=re.U)
    _normalise_re_non_letter_start = re.compile(ur'^\W+', flags=re.U)
    _normalise_re_non_letter_end = re.compile(ur'\W+$', flags=re.U)
    _normalise_re_non_letter = re.compile(ur'\W+', flags=re.U)

    @staticmethod
    def normalise(text, outer=True, inner=False):
        if outer:
            text = wiki._normalise_re_apos1.sub(ur'\1"', text)
            text = wiki._normalise_re_apos2.sub(ur'"\1', text)
            text = wiki._normalise_re_apos3.sub(ur'"', text)
            text = wiki._normalise_re_non_letter_start.sub(ur'', text)
            text = wiki._normalise_re_non_letter_end.sub(ur'', text)
        if inner:
            text = wiki._normalise_re_non_letter.sub(ur'', text)

        return text

if __name__ == '__main__':
    w = wiki("../skwiki-20151226-pages-articles.xml")

    class outter(object):
        def __init__(self):
            self.ls = []
        def write(self, l):
            self.ls.append(l)
        def text(self):
            return "".join(self.ls[1:-1])

    for i, (id, title, page) in enumerate(w.pages()):
        out = outter()
        WikiExtractor.Extractor(id, title, page).extract(out)
        print out.text()
        if i > 5000:
            break
