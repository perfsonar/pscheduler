#!/bin/sh

# CentOS hosts
hostlist="antg-dev.es.net perfsonardev0.internet2.edu test-pt1.es.net antg-staging.es.net perfsonar-dev.grnoc.iu.edu perfsonar-lab-vm.ilab.umnet.umich.edu psps-test2-mgmt.rrze.uni-erlangen.de"

echo "Checking Centos hosts"
echo "_________________________________________________________________________"
for h in $hostlist
do
 echo "Checking for Non-Starters on host $h"
# use this to get description of what failled
 #pscheduler schedule --host $h -PT2H | grep -A 2 Non-Starter
# use this to get a URL to pass to pscheduler result command
 pscheduler schedule --host $h -PT2H | grep -A 3 Non-Starter | grep http
 echo "_________________________________________________________________________"
done

# Debian/Ubuntu hosts
hostlist="ps-4-0.qalab.geant.net pstest.geant.carnet.hr ps-deb-2.es.net"
echo ""
echo "Checking Debian hosts"
echo "_________________________________________________________________________"
for h in $hostlist
do
 echo "Checking for Non-Starters on host $h"
 #pscheduler schedule --host $h -PT2H | grep -A 2 Non-Starter
 pscheduler schedule --host $h -PT2H | grep -A 3 Non-Starter | grep http
 echo "_________________________________________________________________________"
done

