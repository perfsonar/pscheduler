#!/usr/bin/python

#
# Create new test directory from a provided TEMPLATE dir
#

import os
import shutil
import optparse
import sys

def usage():
    print """
    Usage: plugin_dev [test|tool|archiver] [name]

    Examples:
    plugin_dev test ftp
    plugin_dev tool dns
    """

# Gather Args
args = sys.argv[1:]

if args[0] not in [ "test", "tool", "archiver" ]:
    usage()
    exit(1)

type = args[0]
testName = args[1]

dirName = "pscheduler-" + type + "-TEMPLATE"
# Copy everything to a new directory
newDir = dirName.replace("TEMPLATE", testName)
newDir = "../" + newDir
try:
    shutil.copytree(dirName, newDir)
except shutil.Error as e:
    print "Error copying directory: %s" % e
    sys.exit(1)
except OSError as e:
    print "Error copying directory: %s" % e
    sys.exit(1)

os.chdir(newDir)

# Rename directories
for (path, dirs, files) in os.walk("."):
    for dirName in dirs:
        localPath = path + "/" + dirName
        newName = dirName.replace("TEMPLATE", testName)
        os.rename(dirName, newName)

for (path, dirs, files) in os.walk("."):
    for filename in files:
        localPath = path + "/" + filename
        # Find and replace within files
        with open(localPath) as f:
            s = f.read()
        s = s.replace("TEMPLATE", testName)
        with open(localPath, "w") as f:
            f.write(s)
        # Rename all files as necessary
        os.rename(localPath, localPath.replace("TEMPLATE", testName))

print """
    New dir '%s' has been created.

    Please read plugin_dev.README for further instructions.
    """ % newDir
