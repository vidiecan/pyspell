# coding=utf-8
# See main file for licence
# pylint: disable=C0111,W0212
#
import os
import logging

settings = {
    "start_dir": os.path.dirname( os.path.abspath(__file__) ),
    "path_to_project": "../../src",

    "temp_dir": "temp",
    "data_dir": "data",
    "logging_level": logging.INFO,
    "logging_format": "%(asctime)s %(message)s",
}
