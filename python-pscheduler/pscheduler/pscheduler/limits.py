"""
Helper functions for checking limits in the limit-passes module of test plug-ins.

The functions provided are generally organized by the expected data type of the limit 
to be checked. In many cases they make assumptions about field names and other values, but
provide options for overriding those values if so desired. 
"""

from .durationrange import *
from .enummatcher import *
from .ipaddr import *
from .ipcidrmatcher import *
from .numericrange import *
from .psdns import *
from .stringmatcher import *


def check_ip_limit(limit, spec_addr,
                    ip=None, 
                    possible_ip_versions=[4,6]):
    """
    Check an individual IP limit given the hostname and/or IP from the spec.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec_addr: The hostname, IPv4 or IPv6 address from the spec to be checked
        ip: optional. If already resolved, the IPv4 or IPv6 address to check
        possible_ip_versions: optional. list of allowed ip versions for spec

    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if spec_addr is None:
        #if no addr given then quietly exit
        return errors
        
    # resolve to IP
    all_ips = []
    if ip is None:
        #still need to resolve, because source was not specified
        for possible_ip_version in possible_ip_versions:
            resolved = dns_resolve(spec_addr, ip_version=possible_ip_version)
            if resolved:
                all_ips.append(resolved)
        if len(all_ips) == 0:
            errors.append("{1} cannot be resolved to IP address".format(spec_addr))
            return errors
    else:
        #already resolved, so just look at that
        all_ips = [ ip ]
    
    #do match
    matcher = IPCIDRMatcher(limit)
    for candidate_ip in all_ips:
        if not matcher.contains(candidate_ip):
            errors.append("{0} is not in the allowed address range".format(candidate_ip))
    
    return errors

#
# Check source, dest, endpoint limits
#
def check_endpoint_limits(limit, spec, 
                            spec_source="source", 
                            spec_dest="dest",
                            spec_ip_version='ip-version',
                            limit_source="source", 
                            limit_dest="dest",
                            limit_endpoint="endpoint"):
    """
    Checks source, dest and endpoint limits given a spec.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec: The spec to be evaulated
        spec_source: optional. The name of the source field in the spec. Defaults to "source".
        spec_dest: optional. The name of the dest field in the spec. Defaults to "dest".
        spec_ip_version: optional. The name of the ip-version field in the spec. Defaults to "ip-version".
        limit_source: optional. The name of the source field in the limit. Defaults to "source".
        limit_dest: optional. The name of the dest field in the limit. Defaults to "dest".
        limit_endpoint: optional. The name of the endpoint field in the limit. Defaults to "endpoint".
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    
    errors = []
    
    #if no source, dest or endpoint limit then exit immediately
    has_endpoint_limit = False
    for ep_limit in [limit_source, limit_dest, limit_endpoint]:
        if ep_limit in limit: 
            has_endpoint_limit = True
            break
    if not has_endpoint_limit:
        return errors
        
    #init source, dest and ip version
    ip_version = spec.get(spec_ip_version, None)
    possible_ip_versions = [4, 6]
    source  = spec.get(spec_source, None)
    dest    = spec[spec_dest] #required
    source_ip = None
    dest_ip = None
    if source is not None:
        source_ip, dest_ip = ip_normalize_version(source, dest, ip_version=ip_version)
        if source_ip is None or dest_ip is None:
            #no use in proceeding if can't be resolved
            errors.append("{0} {1} and {2} {3} cannot be resolved to IP addresses of the same type".format(spec_source, source, spec_dest, dest))
            return errors
        if ip_version is None:
            ip_version = ip_addr_version(dest_ip)[0]
    if ip_version is not None:
        possible_ip_versions = [ip_version]
        
    #check source limit if any
    if limit_source in limit:
        if source_ip is None:
            errors.append("This test has a limit on the {0} field but the {0} was not specifed. You must specify a {0} to run this test".format(spec_source))
        else:
            errors += check_ip_limit(limit[limit_source], source, ip=source_ip, possible_ip_versions=possible_ip_versions)
    
    #check dest limit if any
    if limit_dest in limit:
        errors += check_ip_limit(limit[limit_dest], dest, ip=dest_ip, possible_ip_versions=possible_ip_versions, )
                
    #check endpoint limit if any
    if limit_endpoint in limit:
        if source is None or check_ip_limit(limit[limit_endpoint], source, ip=source_ip, possible_ip_versions=possible_ip_versions):
            #source does not match
            if check_ip_limit(limit[limit_endpoint], dest, ip=dest_ip, possible_ip_versions=possible_ip_versions):
                #dest does not match
                errors.append("{0} nor {1} matches the IP range set by {2} limit".format(spec_source, spec_dest, limit_endpoint))
    
    return errors

def check_numeric_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks a numeric limit given a spec and field name where the value in the spec is a 
    single number.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        nrange = NumericRange(limit[limit_field]["range"])
        invert = limit[limit_field].get("invert", False)
        contains, message = nrange.contains(spec[spec_field])
        if invert:
            if contains:
                errors.append("{0} {1}".format(description, message))
        else:
            if not contains:
                errors.append("{0} {1}".format(description, message))
    except KeyError:
        pass  # Don't care if not there.
        
    return errors

def check_numeric_range_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks a numeric limit given a spec and field name where the value in the spec is a 
    numeric range.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        nrange = NumericRange(limit[limit_field]["range"])
        invert = limit[limit_field].get("invert", False)
        for bound in ['lower', 'upper']:
            contains, message = nrange.contains(spec[spec_field][bound])
            if invert:
                if contains:
                    errors.append("{0} ({1} bound) {2}".format(description, bound, message))
            else:
                if not contains:
                    errors.append("{0} ({1} bound) {2}".format(description, bound, message))
    except KeyError:
        pass  # Don't care if not there.
    
    return errors

def check_numeric_list_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks a numeric limit given a spec and field name where the value in the spec is a 
    list of numbers.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        contains = spec[spec_field] in limit[limit_field]["match"]
        invert = limit[limit_field].get("invert", False)
        message = limit[limit_field].get("fail-message", "{0} not within limit".format(description))
        if invert:
           if contains:
               errors.append(message)
        else:
           if not contains:
               errors.append(message)
    except KeyError:
        pass  # Don't care if not there.
    
    return errors

def check_duration_limit(limit, spec, limit_field, description=None, spec_field=None, convert_iso=False):
    """
    Checks a duration limit given a spec and field name where the value in the spec is an 
    ISO8601 duration.

    Args:
        limit: The limit definition to uses as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
        convert_iso: optional. Boolean that if true will assume spec is in seconds and convert to ISO8601. Default is False.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        spec_val = spec[spec_field]
        if convert_iso:
            spec_val = "PT{0}S".format(spec_val)
        nrange = DurationRange(limit[limit_field]["range"])
        invert = limit[limit_field].get("invert", False)
        contains, message = nrange.contains(spec_val)
        if invert:
           if contains:
               errors.append("{0} {1}".format(description, message))
        else:
           if not contains:
               errors.append("{0} {1}".format(description, message))
    except KeyError:
        pass  # Don't care if not there.
    
    return errors

def check_boolean_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks a boolean limit given a spec.

    Args:
        limit: The limit definition to use as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        limit_bool = limit[limit_field]['match']
        spec_bool = spec.get(spec_field, False)
        fail_msg = limit[limit_field].get("fail-message", "{0} testing not allowed".format(description))
        if spec_bool != limit_bool:
            errors.append(fail_msg)
    except KeyError:
        pass  # Don't care if not there.
    
    return errors

def check_enum_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks an enumerated list limit given a spec.

    Args:
        limit: The limit definition to use as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        enum = {
            "enumeration": limit[limit_field]["enumeration"],
            "invert": limit[limit_field].get("invert", False),
        }
        match = EnumMatcher(enum)
        fail_msg = limit[limit_field].get("fail-message","IPv{0} is not allowed".format(spec[spec_field]))
        contains = match.contains(spec[limit_field])
        if not contains:
            errors.append("{0} {1}".format(description, fail_msg))
    except KeyError:
        pass  # Don't care if not there.
    
    return errors

def check_string_limit(limit, spec, limit_field, description=None, spec_field=None):
    """
    Checks a string limit given a spec.

    Args:
        limit: The limit definition to use as the evaluation criteria
        spec: The spec to be evaulated
        limit_field: The name of the field in teh limit to be checked.
        description: optional. A human-readble name of the limit to be used in error messages. Defaults to value of limit_field.
        spec_field: optional. The name of the field in the spec to check. Defaults to value of limit_field.
    Returns:
        List of error strings if limit is not passed. Empty list otherwise.
    """
    errors = []
    if description is None:
        description = limit_field
    if spec_field is None:
        spec_field = limit_field
    try:
        match = StringMatcher(limit[limit_field]["match"])
        invert = limit[limit_field].get("invert", False)
        contains = match.matches(spec[spec_field])
        message = limit[limit_field].get("fail-message", "{0} does not match limit".format(description))
        if not contains or (invert and contains):
            errors.append(message)
    except KeyError:
        pass  # Don't care if not there.
    
    return errors
