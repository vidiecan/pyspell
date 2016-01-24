# -*- coding: utf-8 -*-
# author: jm
import logging
import os
import unittest
import time
import testsettings
import sys
src_dir = os.path.join(
    testsettings.settings["start_dir"],
    testsettings.settings["path_to_project"]
)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir )


class test_case( unittest.TestCase ):
    """
        Unified approach to all tests.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(
            level=testsettings.settings["logging_level"],
            format=testsettings.settings["logging_format"]
        )
        logging.getLogger( ).warning( 30 * "<" )
        logging.getLogger( ).warning( "[[ executing tests in [%s] ..", cls.__module__ )
        cls._time = time.time( )
        cls._clean_modules = []
        cls._logger = logging.getLogger()

    @classmethod
    def tearDownClass(cls):
        lasted = time.time( ) - cls._time
        logging.getLogger( ).warning(
            ".. finished tests in [%s] after [%s] seconds ]]", cls.__module__, lasted
        )
        logging.getLogger( ).warning( 30 * ">" )

    def setUp(self):
        self._test_time = time.time( )
        logging.getLogger( ).warning(
            " TEST [%s] STARTED", self.id()
        )

    def tearDown(self):
        lasted = time.time( ) - self._test_time
        logging.getLogger( ).warning(
            " TEST [%s] ENDED in [%s] seconds", self.id(), lasted
        )

    def file(self, path):
        file_path, exists = files.in_data_dir(path)
        self.assertTrue(exists, "could not find testing [%s] file" % path)
        return file_path

    def aff_file(self, specific=None):
        file_path, exists = files.aff_file(specific)
        self.assertTrue(exists, "could not find testing .aff file")
        return file_path

    def dic_file(self, specific=None):
        file_path, exists = files.dic_file(specific)
        self.assertTrue(exists, "could not find testing .dic file")
        return file_path

    def text_file(self, specific=None):
        file_path, exists = files.text_file(specific)
        self.assertTrue(exists, "could not find testing text file")
        return file_path

    def log(self, msg):
        sys.__stdout__.write(msg + "\n")


class files( object ):
    """
        File helper function wrapper.
    """

    @staticmethod
    def aff_file(specific=None):
        basefile = "sk_SK.aff"
        if specific is None:
            file_path, exists = files.in_data_dir(basefile)
        else:
            file_path, exists = files.in_data_dir(os.path.join(specific, basefile))
        return file_path, exists

    @staticmethod
    def dic_file(specific=None):
        basefile = "sk_SK.dic"
        if specific is None:
            file_path, exists = files.in_data_dir(basefile)
        else:
            file_path, exists = files.in_data_dir(os.path.join(specific, basefile))
        return file_path, exists

    @staticmethod
    def text_file(specific=None):
        basefile = "text.txt"
        if specific is None:
            file_path, exists = files.in_data_dir(basefile)
        else:
            file_path, exists = files.in_data_dir(os.path.join(specific, basefile))
        return file_path, exists

    @staticmethod
    def __in_dir(dir_str, file_str, start_path=None):
        """
            Returns tuple (file_name, exists_bool).

            IF start_path is None uses dirname of this file.
        """
        start_path = os.path.abspath( testsettings.settings["start_dir"] ) \
            if start_path is None else start_path
        file_str = os.path.join( start_path, dir_str, file_str )
        return file_str, os.path.exists( file_str )

    @staticmethod
    def in_data_dir(file_str, start_path=None):
        """
            Returns tuple (file_name, exists_bool) of a file in data_dir.
        """
        return files.__in_dir( testsettings.settings["data_dir"], file_str, start_path )
