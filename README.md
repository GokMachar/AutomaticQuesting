# AutomaticQuesting
DFK Automatic Questing 

# Doesn't work on hero in the tavern

# Setup
Install necessary package. If on windows Microsoft Visual C++ 14.0 or greater is required.

```python setup.py install -f```

Setup a user after changing user_defined_parameters.json with your personall data. The *private_dict_path* need to point to a pickled dictionnary in the form {"YOURADDRESS": "YOURPRIVATEKEY"}. You can setup multiple users but will need to change user_defined_parameters.json everytime. On windows, you will need to add the .bat file to the task scheduler.

```python setup_user.py```

# Contributions
ABI and other idea taken from https://github.com/0rtis/dfk
