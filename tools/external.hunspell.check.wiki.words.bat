..\__temp\hunspell\bin\hunspell -i utf-8 -G -d ..\data\hunspell-sk-20110228.sk_SK ..\data\wiki-words.txt  > ..\__output\hunspell.good
..\__temp\hunspell\bin\hunspell -i utf-8 -w -d ..\data\hunspell-sk-20110228.sk_SK ..\data\wiki-words.txt  > ..\__output\hunspell.bad
echo Good cnt
wc -l ..\__output\hunspell.good
echo Bad cnt
wc -l ..\__output\hunspell.bad
pause