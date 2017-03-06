"""
Functions for figuring out common interface operations
"""

import datetime
import netaddr
import netifaces
import os
import pscheduler
import re
import socket



def source_affinity(addr):
    """Easy to use function that returns the CPU affinity
    given an address. Uses source_interface and interface_affinity
    functions call to accomplish, so it's really just a shorthand
    """
    (address, intf) = source_interface(addr)

    if intf is None:
        return None

    return interface_affinity(intf)


def source_interface(addr, port=80):
    """Figure out what local interface is being used to
    get an address.

    Returns a tuple of (address, interface_name)
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((addr,port))

    interface_address = s.getsockname()[0]

    s.close()

    interface_name = address_interface(interface_address)

    if interface_name:
        return (interface_address, interface_name)

    return (None, None)


def address_interface(addr):
    """Given an address, returns what interface
    has this interface, or None
    """

    # make sure we resolve any address to a specific
    # IP address before looking up interfaces
    addr = pscheduler.dns_resolve(addr)
    if addr == None:
        addr = pscheduler.dns_resolve(addr, ip_version=6)

    all_interfaces = netifaces.interfaces()
    for intf in all_interfaces:
        addresses = netifaces.ifaddresses(intf)

        for family in addresses.keys():
            for addr_info in addresses[family]:
                if addr_info['addr'] == addr:
                    return intf

    return None

def interface_affinity(interface):

    """Given an interface name, returns the CPU affinity
    for that interface if available, otherwise
    returns None.

    Note: that this only works on linux. A good todo might be
    to figure out if it could work on other platforms, but
    given the nature of high speed networking it seems
    like it might not be a big deal.
    """

    # if it's a sub interface, we have to look up the 'main'
    # interface for affinity detection
    match = re.search('(.+)\.\d+$', interface)
    if match:
        interface = match.groups()[0]

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





class LocalIPList:
    """
    Self-refrshing list of local IP addresses
    """

    def __init__(
            self,
            refresh=30  # Maximum age in seconds before refresh
    ):
        self.refresh = refresh
        self.addresses = None
        self.expires = None


    def __refresh(self):
        """
        Update the list of local interfaces if needed
        """
        if self.addresses is None \
           or datetime.datetime.now() > self.expires:

            self.addresses = {}

            if_regex = r'%.*$'

            # Netifaces returns a very deep structure.
            for ifhash in [netifaces.ifaddresses(iface)
                           for iface in netifaces.interfaces()]:
                for afamily in ifhash:
                    for iface in ifhash[afamily]:
                        addr = re.sub(if_regex, '', iface["addr"])
                        try:
                            addr_object = netaddr.IPAddress(addr)
                            self.addresses[addr_object] = 1
                        except netaddr.core.AddrFormatError:
                            # Don't care about things that don't look like IPS.
                            pass

            self.expires = datetime.datetime.now() \
                           + datetime.timedelta(seconds=self.refresh)


    def __contains__(self, item):
        """
        Determine if item is in the address list
        """

        self.__refresh()
        item_ip = netaddr.IPAddress(item)
        return item_ip in self.addresses





if __name__ == "__main__":

    for dest in ["www.perfsonar.net",
                 "10.0.2.4"]:
        (addr, intf) = source_interface(dest)
        print "For dest %s, addr = %s, intf = %s" % (dest, addr, intf)


    for interface in ["eth0", "eth1", "lo", "eth1.412", "eth0.120"]:
        affinity = interface_affinity(interface)
        print "interface affinity = %s for %s" % (affinity, interface)



    localips = LocalIPList(refresh=5)

    for addr in ["1.2.3.4", "5.6.7.8", "10.0.0.1", "127.0.0.1"]:
        print addr, addr in localips

