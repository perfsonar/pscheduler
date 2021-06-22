###
# utilities used by twping command
#

from twping_defaults import *
import configparser
import pscheduler 

#Role constants
CLIENT_ROLE = 0
SERVER_ROLE = 1

log = pscheduler.Log(prefix="tool-twping", quiet=True)

##
# Determine whether particpant will act as client or server
def get_role(participant, test_spec):   
#    #Uncomment this when we do multi-participant
#     role = None
#     flip = test_spec.get('flip', False)
#     single_participant_mode = test_spec.get('single-participant-mode', False)
#     if participant == 0:
#         if single_participant_mode:
#             role = CLIENT_ROLE
#         elif flip:
#             role = SERVER_ROLE
#         else:
#             role = CLIENT_ROLE
#     elif participant == 1:
#         if flip:
#             role = CLIENT_ROLE
#         else:
#             role = SERVER_ROLE
#     else:
#         pscheduler.fail("Invalid participant.")
    
    return CLIENT_ROLE

##
# Open config file
def get_config():
    config = None
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except:
        log.warning("Unable to read configuration file %s. Proceeding with defaults.")
    
    return config
