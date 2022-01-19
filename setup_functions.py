# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 09:32:25 2022
Setup the automatic questing
@author: Gok
"""
import sys
import os
import json
import pickle
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

###### USER DEFINE PARAMETERS. ######
user_define_parameters = json.load(open(f'{__location__}/user_defined_parameters.json', "r"))
USER = user_define_parameters["user"]
RPC = user_define_parameters["rpc"]
PRIVATE_DICT_PATH = user_define_parameters["private_dict_path"]
OS = user_define_parameters["os"]
POOLS = user_define_parameters["pools"]
ADDRESS = user_define_parameters["address"]
BLOCKS = user_define_parameters["blocks"]

def metadata_setup():
    # Create empty folder for the user.
    os.makedirs(f"{__location__}/{USER}", exist_ok = True)
    
    autoquester_meta = {"rpc": RPC, "os": OS, "private_dict_path": PRIVATE_DICT_PATH,
                        USER: {"pools": POOLS, "address": ADDRESS},
                        "pools": {"JEWEL-ONE": 0, "JEWEL-BUSD": 1, "JEWEL-bscBNB": 2,
                                  "JEWEL-1ETH": 3, "ONE-BUSD": 4, "JEWEL-XYA": 5,
                                  "JEWEL-1USDC": 6, "JEWEL-1WBTC": 7, "JEWEL-UST": 8,
                                  "ONE-1ETH": 9, "ONE-1USDC": 10, "1WBTC-1ETH": 11,
                                  "JEWEL-1SUPERBID": 12, "ONE-1SUPERBID": 13,
                                  "JEWEL-MIS": 14, "JEWEL-AVAX": 15, "JEWEL-FTM": 16,
                                  "JEWEL-LUNA": 17, "JEWEL-MATIC": 18},
                        "iquesting_address": '0x5100bd31b822371108a0f63dcfb6594b9919eaf4',
                        "quest_dict": {"foraging": "0x3132c76acF2217646fB8391918D28a16bD8A8Ef4",
                                       "fishing": "0xE259e8386d38467f0E7fFEdB69c3c9C935dfaeFc",
                                       "gardening": "0xe4154B6E5D240507F9699C730a496790A722DF19",
                                       "mining": '0x6FF019415Ee105aCF2Ac52483A33F5B43eaDB8d0'}}
    pickle.dump(autoquester_meta, open(f"{__location__}/{USER}/{USER}_meta.pk", "wb"))

def setup_script():
    file = open(f"{__location__}/{USER}/{USER}_quest.py", "w") 
    file.write(f"""
#-*- coding: utf-8 -*-
#@author: Gok
import sys
import os
import pickle
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(current))
from AutoForagingFishing import FastQuest 
from AutoMiningGardening import SlowQuest

user = "{USER}"
fast = FastQuest(user)
slow = SlowQuest(user, {BLOCKS})

fast.complete_all_quest()
slow.complete_all_quest()

slow.start("mining")
slow.start("gardening")

fast.start("fishing")
fast.start("foraging")
""") 
    file.close() 

def setup_scheduler_script():
    if OS == "windows":
        file = open(f"{__location__}/{USER}/{USER}_quest_schedule.bat", "w") 
        file.write(f"""start {sys.executable} {__location__}\{USER}\{USER}_quest.py""") 
        file.close() 
    else:
        print("No need for .bat on linux")

def setup_crontab():
    print("Wait")









