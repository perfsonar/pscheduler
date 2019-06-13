# General pScheduler Plugin Development Guide ###

### 1. Create desired test/tool/archiver directories using the plugin_dev.py script.

```
Usage: plugin_dev [test|archiver] [name]                                       
       plugin_dev [tool] [test-associated] [name]
```

### 2. Go to the tool directory and open the files 'can-run' and 'enumerate'. 
There are fields in each file marked 'EDIT ME', which should
be changed to match the name of the test you just created. These files
should also be commented with instruction.

### 3. In the root directory of the test and the tool, run the following command
```
sudo make cbic
```
Having done this, a basic idling plugin will have been built into pSschduler.
Run 'pscheduler task [name] --help' to see its usage case. Running 
'pscheduler plugins [tests|tools]' should show the new plugin in the list
of tests/tools.

### 4. Now, start in the root of the test directory and run the following:
```
grep -R Order *
```
According to the order number of the files, each one should then be
visited and changed, if deemed necessary. Each one will be commented
at the top, as well as throughout.

### 5. Do the same with the tool, running 
```
grep -R Order *
```
in its root directory to start.

## Notes

- Any time you wish to test the plugin through pScheduler itself, just
run 'make cbic' in the test and tool root directories to rebuild. If you're
getting unusual behavior, sometimes rebuildling pScheduler itself can be
helpful.

- Testing of the tool independent of the test can be usefull for debugging. Enter the tool's subdirectory and pipe json input into the run file. This command will return the result of the tool's execution.
```
./run < example_input.json 
```

- Testing of a specific tool and test combination can be done with the following command. Replace the text in all caps.
```
pscheduler task --tool TOOL TEST --ARGUMENTS
```

- It is recommened that you first test several of the files by directly
piping json into them. It's much more convenient than rebuilding into
pScheduler, and will be easier to immediately diagnose.
For example, 
```
./cli-to-spec --arg options | ./spec-format
```

- To see the run results of a pScheduler run, run
```
curl -s -k
```
on the Task URL. This will be output in JSON, which can be piped into
a file or into something like JQ for readability

-More extensive documentation on developing archivers can be found in the archiver template folder. Below is more extensive documentation on developing tests and tools

# Developing

## Tests

Running the grep command from step 4 will result in a list of all the files that need to be developed, with an order next to them. It's recommend that you develop in that order. The files are listed below in development order, along with a short description of what goes in each file.

### RPM spec file 

This file governs the RPM build of your test. The template will set up everything you need, so there should be nothing you need to change in this file. You should check this file first, looking to make sure that the template filled in the name fields correctly with the name of your test. 

### enumerate

This file is also nearly complete, but you should check it for name accuracy as well. Also add a description of your test and what it does.

### validate.py

This file is where the JSON spec for your test is defined. Before writing this file, you should have a clear idea of what you want the input and output JSON of your test to look like. This file contains some code designed to make the test and tool work out of the box with idle. There are comments in the file outlining what should not be removed (i.e. what is considered important and necessary for all pScheduler tests), but everything else is simply there for the idle test and can be replaced with the options you want to include for your test.

### cli-to-spec

This file takes the arguments given when the test is invoked in the command line and converts them to the test's JSON spec. Make sure you have written ```validate.py``` before writing this file so that you have a clear JSON schema to use. The options used in ```cli-to-spec``` need to be the same as those in ```validate.py```.

### spec-to-cli

This file does the inverse of ```cli-to-spec```, it turns the JSON spec into a list of command line arguments. Make sure to continue using the same schema and to test these files as you go for typos/misalignment.

### spec-is-valid

This file verifies that a given spec is valid according to the test. It's a good idea to test this with the output from ```cli-to-spec```.

### participants

If you are writing a single participant test (only one perfSONAR node is involved, you probably do not need to edit this file. If you have multiple nodes participating in your test, you'll need to edit this file to reflect that. For guidance, look to tests such as thoroughput which have multiple nodes involved.

### result-format

This file formats the result JSON into plain text or html output. You can format your output how you like, making sure to follow the result spec you outlined in ```validate.py```. Examples can be found in other tests.

### spec-format

This is similar to ```result-format``` but for the input spec instead of the output. It formats the spec JSON into plain text or html output.

## Tools

### spec file

Similar to this test, you likely will not need to edit this file but you should review it to make sure the template inserted everything correctly.

# Testing

## Tests

### cli-to-spec

You can test this file directly in the command line by using ```./cli-to-spec --option argument```

### spec-to-cli

You need to have a working ```cli-to-spec``` file before you can test this file in the command line. Once you do, you can simply run the same command used to test ```cli-to-spec``` and simply pipe it into ```spec-to-cli``` : ```./cli-to-spec --option argument | ./spec-to-cli```

### spec-is-valid

You can test this in a similar manner to ```spec-to-cli``` using the following command: ```./cli-to-spec --option argument | ./spec-is-valid```

### result-format

In order to test this, you need to already have some result JSON generated. Once you do, you can test the formatting simply by using ```cat result_json | ./result-format text/html``` or ```cat result_json | ./result-format text/plain``` depending on if you want the result formatted as html or plain text.

### spec-format

To test this, you can generate a spec using ```cli-to-spec``` as shown above and then simply pipe it into ```spec-format```. ```./cli-to-spec --option argument | ./spec-format``` will give the plain text formatting while ```./cli-to-spec --option argument | ./spec-format text/html``` will give the html version.

## Troubleshooting: Common Errors and How to Solve Them

Test fails when run out of box (no non-template changes) with the following error:

``Submitting task...
Unable to post task: Unable to complete request: No tool in common among the participants:  localhost offered nothing.
The 'pscheduler troubleshoot' command may be of use in problem
diagnosis. 'pscheduler troubleshoot --help' for more information``

This error indicates that the tool does not recognize the test/think it can run it. A common cause of this is a mismatched test/tool name. You can run ```pscheduler plugins tools``` to see if your tool recognizes that the test belongs to it (and to check for naming/spelling errors). If it doesn't recognize it or it is misnamed, you'll need to edit the ```enumerate``` and ```can-run``` files for the tool to contain the correct test name.
