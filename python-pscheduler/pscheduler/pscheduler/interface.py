"""
Functions for figuring out common interface operations
"""

import netifaces
import os
import socket

# Return what interface is being used to get to a particular
# address
def source_interface(addr, port=80):
    """Figure out what local interface is being used to 
    get an address.

    Returns a tuple of (address, interface_name)
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((addr,port))

    interface_address = s.getsockname()[0]

    s.close()

    interface_name = None

    all_interfaces = netifaces.interfaces()
    for intf in all_interfaces:
        addresses = netifaces.ifaddresses(intf)

        for family in addresses.keys():
            for addr_info in addresses[family]:
                if addr_info['addr'] == interface_address:
                    return (interface_address, intf)

    return (None, None)


def interface_affinity(interface):
    
    """Given an interface name, returns the CPU affinity
    for that interface if available, otherwise
    returns None.

    Note: that this only works on linux. A good todo might be
    to figure out if it could work on other platforms, but
    given the nature of high speed networking it seems
    like it might not be a big deal.
    """

    filename = "/sys/class/net/%s/device/numa_node" % interface

    if not os.path.exists(filename):
        return None

    with open(filename,'r') as f:
        affinity = f.read().rstrip()

        # This is the same as no affinity, so make calling
        # functions not care
        if affinity == "-1":
            return None

        return affinity

    return None


if __name__ == "__main__":

    for dest in ["www.perfsonar.net",
                 "10.0.2.4"]:
        (addr, intf) = source_interface(dest)
        print "For dest %s, addr = %s, intf = %s" % (dest, addr, intf)


    for interface in ["eth0", "eth1", "lo"]:
        affinity = interface_affinity(interface)
        print "interface affinity = %s for %s" % (affinity, interface) 
