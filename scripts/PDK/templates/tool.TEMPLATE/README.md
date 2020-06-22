## Creating and Understanding a pScheduler Tool

## Anatomy of a Tool

### enumerate

Most of this is filled in by the PDK. You'll need to edit the description and make sure the 'tests' field is accurate. That specifies what tests the tool is compatible with. You'll want to be absolutely sure that the test named in there is the test you're co-developing with the tool. If you're adding a tool for a pre-existing test, make sure it's accurate.

### can-run 

You will probably not have to edit this file after PDK generation. This file determines if the tool can be run under the given circumstances. It's important to check that the test name in can-run matches the actual test name. Otherwise, it will refuse to run with the test and give an error message saying it's incompatible.

### duration

This file determines the duration of the specified test. You'll want to designate an appropriate default timeout period for your test here.

### run

This is where the majority of the development for the tool takes place. The code to actually run the tool is written here. Everything that is needed to successfully complete the given test with the given tool needs to be here. This is the file that will invoke the actual program the tool is written around or be the complete python script to execute the task.


