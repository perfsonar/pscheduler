#!/usr/bin/python

#
# Create new test directory from a provided TEMPLATE dir
#

import os
import shutil
import optparse
import sys

# Gather Args
args = sys.argv[1:]

parser = optparse.OptionParser()

# Add Options
parser.add_option("-d", "--dir", dest="directory",
                  help="Source directory to be copied from.",
                  action="store", type="string")

parser.add_option("-t", "--test-name", dest="testname",
                  help="Name of new test type.",
                  action="store", type="string")

# Parse Options
(options, args) = parser.parse_args(args)

if options.directory is not None:
    dirName = options.directory
else:
    parser.error("Directory name not given.")

if options.testname is not None:
    testName = options.testname
else:
    parser.error("Test naem not given.")

# Copy everything to a new directory
newDir = dirName.replace("TEMPLATE", testName)
newDir = "../" + newDir
try:
    shutil.copytree(dirName, newDir)
except shutil.Error as e:
    print """Directory not copied. Please choose one of pscheduler-test|tool|archiver-TEMPLATE. 
    Error: %s""" % e
    sys.exit(1)
except OSError as e:
    print """Directory not copied. Please choose one of pscheduler-test|tool|archiver-TEMPLATE.
    Error %s""" % e
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
