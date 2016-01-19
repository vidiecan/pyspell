@echo off

set TO_TEST=../../../../src
set IGNORE="E111,E201,E211,E303,W291,E203,E221,E501,E202"
set EXCLUDE=twill,cherrypy,coverage,docs,_tests,subprojects,httplib2,pympler,dateutil,requests

python "%~dpn0".py  --show-pep8  --exclude=%EXCLUDE% --ignore=%IGNORE% --statistics --filename=*.py %TO_TEST%