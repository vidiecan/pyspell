@echo off

set TO_TEST=pyspell

python "%~dpn0" --rcfile=%~dp0\\pylint.rcfile %TO_TEST% | grep -v "Locally disabling"

