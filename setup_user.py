# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 12:24:35 2022
@author: Gok
"""
import sys
import os
import json
from UserWeb3 import UserWeb3
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
user_define_parameters = json.load(open(f'{__location__}/user_defined_parameters.json', "r"))
user = UserWeb3(user_define_parameters["user"])
