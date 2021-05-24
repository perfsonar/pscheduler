# pScheduler Development Cluster

This Vagrantfile builds a cluster of VirtualBox VMs for pScheduler
development with the following features:

 * User account to match the one that invoked Vagrant
 * User's home directory shared into the VM
 * User account given full, passwordless access to sudo
 * Pre-created local storage area in `/local/<username>`
 * Private network segment for the cluster
 * IPv4 network between VMs
 * IPv6 network between VMs (TODO: Not currently working)
 * VM hostnames available in `/etc/hosts`

This works on Linux and MacOS and has not been tested on Windows.

**NOTE:** On some systems, pScheduler fails to build in the shared
file system where the user's home directory resides but builds fine on
the guest's "native" file space.  This is likely a problem with
VirtualBox rather than Vagrant or this configuration and will be
investigated further.  Until this is resolved, the recommended
workaround is to do development done in `/local/<username>`.


## Prerequisites

Your system must have the following installed:

 * VirtualBox
 * Vagrant
 * Ansible


## Setup

The default is to build a single-host cluster of CentOS 7 systems, which
can be done by running `vagrant up`.

Several things in `Vagrantfile` can be customized; see the top of
that file for more information.


## Logging in

Log in with
```
vagrant ssh -c "exec sudo su - `id -un`" HOSTNAME
```
where `HOSTNAME` is the name of a host.


Here are some convenient Bourne shell aliases:
```
# Regular SSH
alias vssh='vagrant ssh'

# SSH, become root
alias vsshr='vagrant ssh -c "sudo -i"'

# SSH, become $USER
alias vsshu='vagrant ssh -c "sudo -i -u ${USER}"'
```


## Teardown

Destroy the cluster with 'vagrant destroy -f'.
