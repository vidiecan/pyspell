python -m cProfile -o pywiki-words.prof do.py --unknown-from-wiki
snakeviz pywiki-words.prof
pause