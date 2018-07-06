#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import getopt
import json
import os
import sys
import logging
import time
from collections import defaultdict

_logger = None

__this_dir = os.path.dirname(os.path.abspath(__file__))
__log_dir = os.path.join(__this_dir, "__logs")

settings = {
    "settings": "../settings.json",
    "log_every_n": 10000,
    "runnable": {},
    "tasks": {
        "valid-words": [None, 100, 90, 80, 70, 60, 40, 20],
    },
    "logger": {
        "version": 1,
        "log_dir": __log_dir,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "detailed",
                "filename": os.path.join(__log_dir, "%s.%s.log"),
                "level": "INFO",
            },
        },
        "loggers": {
            "": {
                "handlers": ["file", "console"],
                "level": "INFO",
            },
        },
        "formatters": {
            "detailed": {
                "format": "%(asctime)s,%(msecs)03d %(levelname)-5.4s" +
                          " [%(name)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }
    }
}


def help(env):
    print "Possible options:"
    print "\n".join(env["runnable"].keys())


def parse_settings():
    """ Parses the global setting json and updates the local settings. """
    env = settings
    if os.path.exists(env["settings"]):
        settingsd = json.load(open(env["settings"], "r+"))
        settings_dir = os.path.dirname(env["settings"])
        settingsd["start_dir"] = os.path.abspath(settings_dir)
        env.update(settingsd)
    return env


def parse_command_line():
    """ Parses the command line arguments. """
    env = parse_settings()

    opts = None
    try:
        options = env["runnable"].keys()
        input_options = sys.argv[1:]
        opts, _ = getopt.getopt(input_options, "", options)
    except getopt.GetoptError, e:
        pass

    what_to_do = help
    for option, param in opts:
        option = option[2:]
        if option in env["runnable"]:
            what_to_do = env["runnable"][option]

    return what_to_do, env


# ========================
# Helpers
# ========================

min_occurrences = settings["tasks"]["valid-words"]


def _is_important_valid_word(word, f, non_sk_words):
    dyn_min_occurrences = min_occurrences[min(len(min_occurrences) - 1, len(word))]
    if dyn_min_occurrences <= f:
        if non_sk_words(word):
            # important and non valid
            return True, False
        # important and valid
        return True, True
    # not important for now and we do not know if valid
    return False, None


def _init_logging(env, what_to_do):
    import logging.config
    if "log_dir" in env["logger"]:
        if not os.path.exists(env["logger"]["log_dir"]):
            try:
                os.makedirs(env["logger"]["log_dir"])
            except Exception, e:
                pass
    env["logger"]["handlers"]["file"]["filename"] = \
        env["logger"]["handlers"]["file"]["filename"] % (
            time.strftime("%Y-%m-%d-%H.%M.%S"), what_to_do
        )
    logging.config.dictConfig(env["logger"])


# ========================
# Real functionality
# ========================

def unknown_from_wiki(env):
    """
        How many words do we know from a list of most used ones?
    """
    sys.path.insert(0, os.path.join(env["start_dir"], env["src_dir"]))

    def _progress(cnt, cnt_nf, cnt_nf_f_cap, time_arr):
        time_arr.append(time.time())
        return "in [%.2fs] .. done [%8d] words ... [%5d][%.2f%%] not found ... " \
               "[%5d][%.2f%%] not found lower" % (
                   (time_arr[-1] - time_arr[-2]),
                   cnt,
                   cnt_nf, (100. * cnt_nf / cnt),
                   cnt_nf - cnt_nf_f_cap, (100. * (cnt_nf - cnt_nf_f_cap) / cnt)
               )

    dictionaries = env["input"]["dictionaries"]
    aff_file = os.path.join(env["start_dir"], env["input"]["dir"], dictionaries + ".aff")
    dic_file = os.path.join(env["start_dir"], env["input"]["dir"], dictionaries + ".dic")
    wiki_words_input = os.path.join(env["start_dir"], env["output"]["dir"], env["output"]["wiki_words"])
    log_every_n = env["log_every_n"]
    wiki_not_found_output = os.path.join(env["start_dir"], env["temp"]["dir"], env["temp"]["wiki_not_found"])

    if not os.path.exists(aff_file):
        raise Exception("AFF file not found [%s]" % aff_file)
    if not os.path.exists(dic_file):
        raise Exception("DIC file not found [%s]" % dic_file)
    if not os.path.exists(wiki_words_input):
        raise Exception("Wiki words input not found [%s]" % wiki_words_input)

    from pyspell import speller
    s = speller(aff_file, dic_file)
    s.init()

    ignorecase = False

    pos = 0
    not_found = 0
    not_found_first_cap = 0
    time_arr = [time.time()]

    _logger.info("Checking words...")
    with codecs.open(wiki_not_found_output, mode="w+", encoding="utf-8") as fout:
        with codecs.open(wiki_words_input, mode="r+", encoding="utf-8") as fin:
            not_found_arr = []
            for l in fin:
                pos += 1
                l = l.strip()
                ret = s.check(l, ignorecase)
                if ret is None:
                    not_found += 1
                    if l[0].isupper():
                        not_found_first_cap += 1
                    # _logger.info(u"Not found: [%s]", l)
                    not_found_arr.append(l)
                    for i in range(100):
                        if 10000 < len(not_found_arr):
                            # similar to u'\n'.join()
                            fout.writelines(not_found_arr)
                        not_found_arr = []
                if 0 == pos % log_every_n:
                    _logger.info(_progress(pos, not_found, not_found_first_cap, time_arr))
            fout.writelines(not_found_arr)
    _logger.info(_progress(pos, not_found, not_found_first_cap, time_arr))


def wiki_freqs(env):
    """
        Gather the freqs of words from a wiki.

        Note: not tested with larger wikis!
    """
    from pyspell._utils import non_sk_words

    wiki_out_freqs = os.path.join(env["start_dir"], env["output"]["dir"], env["output"]["wiki_freqs"])
    if not os.path.exists(wiki_out_freqs):
        raise Exception("Wiki freqs not found [%s]" % wiki_out_freqs)
    freqs_d = json.load(open(wiki_out_freqs, "rb"))

    def _words():
        wiki_words_output = os.path.join(env["start_dir"], env["output"]["dir"], env["output"]["wiki_words"])
        with codecs.open(wiki_words_output, mode="w+", encoding="utf-8") as fout:
            cnt_done = 0
            cnt_ignored = 0
            _logger.info("Collecting words...")
            for word, freq in freqs_d.iteritems():
                is_important, is_valid = _is_important_valid_word(word, freq, non_sk_words)
                if is_important and is_valid:
                    cnt_done += 1
                    fout.write(word + u"\n")
                else:
                    cnt_ignored += 1
        _logger.info("Sorting...")
        with codecs.open(wiki_words_output, mode="r+", encoding="utf-8") as fin:
            lines = sorted(fin.readlines())
        with codecs.open(wiki_words_output, mode="w+", encoding="utf-8") as fout:
            fout.writelines(lines)

        _logger.info("Done [%d] words, ignored [%d] words", cnt_done, cnt_ignored)

    def _stats():
        check_length = range(6, 12)
        d = {}
        for i in check_length:
            d[i] = defaultdict(int)
        for k, v in freqs_d.iteritems():
            if len(k) in check_length:
                d[len(k)][v] += 1
        max_output_freq = 40
        for wlen, v in d.iteritems():
            print "Words with length: [%d]" % wlen
            for freq, cnt in v.iteritems():
                print "  [%d] words occurred [%d]-nth times in input data" % (cnt, freq)
                if freq > max_output_freq:
                    break

    _words()


def wiki_stats(env):
    """
        Basic statistics from a wiki.

        Note: not tested with larger wikis!
    """
    from pyspell._utils import non_sk_words
    from simplewiki import wiki

    wiki_input = os.path.join(env["start_dir"], env["input"]["dir"], env["input"]["wiki_xml"])
    wiki_out_freqs = os.path.join(env["start_dir"], env["output"]["dir"], env["output"]["wiki_freqs"])
    if not os.path.exists(wiki_input):
        raise Exception("Wiki input not found [%s]" % wiki_input)
    w = wiki(wiki_input)
    freqs = defaultdict(int)
    all_words = 0
    log_every_n = env["log_every_n"]
    for pos, (wordorig, word, sentence_start, page_id) in enumerate(w.words(True)):
        if 0 == len(word) or non_sk_words(word):
            continue
        word = word.lower()
        all_words += 1
        freqs[word] += 1
        if 0 == all_words % log_every_n:
            perc = round((100. * float(len(freqs))) / all_words, 3)
            _logger.info(
                    "done [%8d] words ... [%8d][%.2f%%] unique words ... [%5d] pages",
                    all_words, len(freqs), perc, page_id
            )

    print "   # of all words: %6d" % all_words
    print "# of unique words: %6d" % len(freqs)
    import heapq
    nth = 100
    too_few_occurrences = 20
    baseline = heapq.nlargest(nth, freqs.values())[-1]
    d = defaultdict(list)
    min_occurs_cnt = 0
    min_occurrences = [None, 100, 90, 80, 70, 60, 40, 20]
    min_occurrences_freq = defaultdict(int)
    json.dump(freqs, open(wiki_out_freqs, "w+"), encoding="utf-8")
    for k, v in freqs.iteritems():
        too_few_occurrences = min_occurrences[min(len(min_occurrences) - 1, len(k))]
        if v < too_few_occurrences:
            min_occurrences_freq[len(k)] += 1
            min_occurs_cnt += 1
        if v >= baseline:
            d[v].append(k)
    print "# of unique words that occurred < %d times: %6d" % (
        too_few_occurrences, min_occurs_cnt
    )

    for k, v in min_occurrences_freq.iteritems():
        print "Words with len [%3d] occurred < too_few_occurrences [%4d] times" % (k, v)

    for k in sorted(d.keys(), reverse=True):
        for v in d[k]:
            print "%6s: %4d" % (v, k)


def wiki_words(env):
    """
        Gather most used words according to a specific definition
        Note: not tested with larger wikis!
    """
    from simplewiki import wiki
    from pyspell._utils import non_sk_words

    wiki_input = os.path.join(env["start_dir"], env["input"]["dir"], env["wiki_xml"])
    wiki_words_output = os.path.join(env["start_dir"], env["output"]["dir"], env["output"]["wiki_words"])
    log_every_n = env["log_every_n"]
    if not os.path.exists(wiki_input):
        raise Exception("Wiki input not found [%s]" % wiki_input)
    w = wiki(wiki_input)

    done_occurrence = 1234567
    freqs = defaultdict(int)
    capital_freqs = defaultdict(int)
    with codecs.open(wiki_words_output, mode="w+", encoding="utf-8") as fout:
        for pos, (wordorig, word, sentence_start, page_id) in enumerate(w.words(True)):
            if 0 == len(word):
                continue
            f = freqs[word]
            # skip already done or strange
            if done_occurrence == f or 0 > f:
                continue

            if sentence_start and word[0].isupper():
                capital_freqs[word] += 1
                continue

            freqs[word] = f + 1
            is_important, is_valid = _is_important_valid_word(w, f, non_sk_words)
            if is_important:
                if not is_valid:
                    # do not bother with that one again
                    freqs[word] = -1
                    continue
                freqs[word] = done_occurrence

                # have we already output the same but lowercase?
                if not word.islower() and done_occurrence == freqs[word.lower()]:
                    _logger.warn(u"Processing non-lower word [%s] but lower has been already processed", word)

                if word.islower() and done_occurrence == freqs[word[0].upper() + word[1:]]:
                    _logger.warn(u"Processing lower word [%s] but non-lower has been already processed", word)

                if not word.islower():
                    iword = word.lower()
                    iwordfreq = freqs[iword]
                    if 0 < iwordfreq and float(f) / float(iwordfreq) <= 2.:
                        _logger.warn(
                                u"Capital first being processed [%s][%d] but non capital is not 0 [%d]",
                                word, f, iwordfreq
                        )
                    if word in capital_freqs:
                        del capital_freqs[word]

                fout.write(word + u"\n")
                if 0 == pos % log_every_n:
                    _logger.info("done [%8d] words ... [%5d] pages", pos, page_id)

    _logger.info("Could not get capitals right:")
    for k, v in capital_freqs.iteritems():
        if v > min_occurrences[-1] / 3:
            if non_sk_words(k):
                continue
            if done_occurrence == freqs[k.lower()]:
                continue
            _logger.info("%10s: %2d", k, v)


def morpho_parse(env):
    """
        Gather most used words according to a specific definition
        Note: not tested with larger wikis!
    """
    import glob
    from simplemorpho import morpho, word_forms

    input_glob = os.path.join(
            env["start_dir"],
            env["input"]["dir"],
            env["input"]["morpho_glob"]
    )
    for f in glob.glob(input_glob):
        _logger.info(u"Working on [%s]", f)
        m = morpho(f)
        max_show = 0
        m.parse(all_forms=True, max_process=max_show)

        ##
        if True:
            sys.path.insert(0, os.path.join(env["start_dir"], env["src_dir"]))
            dictionaries = env["input"]["dictionaries"]
            aff_file = os.path.join(env["start_dir"], env["input"]["dir"], dictionaries + ".aff")
            dic_file = os.path.join(env["start_dir"], env["input"]["dir"], dictionaries + ".dic")
            from pyspell import speller
            s = speller(aff_file, dic_file)
            s.init()
            pos = 0
            for k in s._dic._d.keys():
                if k.lower() not in m.all_forms():
                    _logger.info(u"Word from .dic not found in ma [%s]", k)
                    pos += 1
            print "Not found words [%d out of %d]" % (pos, len(s._dic._d))



        ##
        uniq_rules = set()
        uniq_rules_right = set()
        for pos, (k, v) in enumerate(m.forms().iteritems()):
            if 0 < max_show < pos:
                break
            #print u"%s: %s" % (k, u",".join(v.forms()))
            #print v.rules()
            r_strs = word_forms.rule_strs(v.rules())
            uniq_rules |= set(r_strs)
            uniq_rules_right |= set([x.split("->")[0] for x in r_strs])

        msg = "All rules [%d], unique rules [%d], unique rules right [%d]" % (
            pos, len(uniq_rules), len(uniq_rules_right)
        )
        print msg
        for pos, r in enumerate(sorted(uniq_rules)):
            if 1000 < pos:
                break
            print r
        print msg



if __name__ == "__main__":
    settings["runnable"] = {
        "unknown-from-wiki": unknown_from_wiki,
        "wiki-stats": wiki_stats,
        "wiki-words": wiki_words,
        "wiki-freqs": wiki_freqs,
        "morpho": morpho_parse,
    }

    what_to_do, env = parse_command_line()
    _init_logging(env, what_to_do.__name__)
    _logger = logging.getLogger()
    _logger.info("Starting...")
    lasted = time.time()
    what_to_do(env)

    lasted = time.time() - lasted
    _logger.info("Finished in [%.3fs]...", lasted)
