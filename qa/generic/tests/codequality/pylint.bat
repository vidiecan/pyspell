@echo off

set TO_TEST=pyspell
set IGNORE=""

python "%~dpn0" --ignore=%IGNORE% --rcfile=%~dp0\\pylint.rcfile %TO_TEST% | grep -v "Locally disabling"

