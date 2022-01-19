# AutomaticQuesting
DFK Automatic Questing 

# Doesn't work on hero in the tavern

# How to set up the json.
- user : Your user name (e.g. "Tomas")
- rpc : Your preferred rpc (e.g. "https://api.fuzz.fi/")
- private_dict_path : Path to a pickled dictionnary (your can create this with these commance from command line)

```pyton```

```import pickle```

```private_dict = {"youraddress": "yourprivatekey"}```

```pickle.dump(private_dict, open(private_dict_path, "wb"))```

- os : Your operating system (only windows for now, "window")
- pools : Your liquidity pool position, you will need to put one if you have a gardenener, even if you don't have a position (e.g. ["JEWEL-ONE"])
- address : Your checksumed address (can copy from metamask e.g. "0xC5375B0A1Da8933c94b7d6d537FEb2c4C80d9347")
- blocks : Nuumber of block you wish your gardenenr and miners to stop their quests (maximizes Jackpot, e.g. 15 or "MAX" for the full quest)

```{"user": "Tomas", "rpc": "https://api.fuzz.fi/", "private_dict_path": "C://abl.pickled_dict.pk", "os": "windows", "pools": ["JEWEL-ONE"], "address": "0xC5375B0A1Da8933c94b7d6d537FEb2c4C80d9347", "blocks": "MAX"}```

# Setup
Install necessary package. If on windows Microsoft Visual C++ 14.0 or greater is required.

```python setup.py install -f```

Setup a user after changing user_defined_parameters.json with your personall data. The *private_dict_path* need to point to a pickled dictionnary in the form {"YOURADDRESS": "YOURPRIVATEKEY"}. You can setup multiple users but will need to change user_defined_parameters.json everytime. On windows, you will need to add the .bat file to the task scheduler.

```python setup_user.py```

# Contributions
ABI and other idea taken from https://github.com/0rtis/dfk
