###
# utilities used by owping command
#

CLIENT_ROLE = 0
SERVER_ROLE = 1
def get_role(participant, test_spec):   
    role = None
    flip = test_spec.get('flip', False)
    single_participant_mode = test_spec.get('single-participant-mode', False)
    if participant == 0:
        if single_participant_mode:
            role = CLIENT_ROLE
        elif flip:
            role = SERVER_ROLE
        else:
            role = CLIENT_ROLE
    elif participant == 1:
        if flip:
            role = CLIENT_ROLE
        else:
            role = SERVER_ROLE
    else:
        pscheduler.fail("Invalid participant.")
    
    return role