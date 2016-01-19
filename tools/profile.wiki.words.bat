python -m cProfile -o pywiki-words.prof do.py --wiki-words
snakeviz pywiki-words.prof
pause