# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 12:24:35 2022
@author: Gok
"""
import sys
import os
import json
from UserWeb3 import UserWeb3
from setup_functions import setup_script, setup_scheduler_script, metadata_setup
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
user_define_parameters = json.load(open(f'{__location__}/user_defined_parameters.json', "r"))
metadata_setup()   
setup_script()
setup_scheduler_script()