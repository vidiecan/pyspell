@echo off

set TO_TEST=../../../../src/pyspell
set IGNORE="E111,E201,E211,E303,W291,E203,E221,E501,E202"
set EXCLUDE=

python pep8.py --show-pep8  --exclude=%EXCLUDE% --ignore=%IGNORE% --filename=*.py %TO_TEST%
echo done.
pause