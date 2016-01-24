[![Build Status](https://travis-ci.org/vidiecan/pyspell.svg?branch=master)](https://travis-ci.org/vidiecan/pyspell)

pyspell
=======

Pure python reimplementation of a limited set of hunspell (https://github.com/hunspell/hunspell) functionality.
Only a limited set of .aff features are supported and the dictionaries have to be encoded in UTF-8.

Usage
-----

See qa/unittests or simply:

```
    from pyspell import speller
    s = speller(aff_file, dic_file)
    s.init()
    if s.check("something") is None:
        print "Not found"
```


Performance
-----------
This is an optimised version that parses 80.000 words with a normal dictionary in approx. 6 seconds
including dictionary parsing.
The first version performed the same task on the same machine in 150 seconds.

Tools
-----

If you want to use the functionality from the tools directory, update settings.json accordingly. You can use
dictionaries from http://www.sk-spell.sk.cx/.

Note: Verify you really want to use `non_sk_words` for non SK wikis.


Note
----
Inspiration is taken from the original hunspell c++ implementation.
