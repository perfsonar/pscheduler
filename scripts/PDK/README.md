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

# Developing

## Tests

Running the grep command from step 4 will result in a list of all the files that need to be developed, with an order next to them. It's recommend that you develop in that order.

# Testing

## Testing a test

### cli-to-spec

You can test this file directly in the command line by using ```./cli-to-spec --option argument```

## Troubleshooting: Common Errors and How to Solve Them

Test fails when run out of box (no non-template changes) with the following error:

``Submitting task...
Unable to post task: Unable to complete request: No tool in common among the participants:  localhost offered nothing.
The 'pscheduler troubleshoot' command may be of use in problem
diagnosis. 'pscheduler troubleshoot --help' for more information``

This error indicates that the tool does not recognize the test/think it can run it. A common cause of this is a mismatched test/tool name. You can run ```pscheduler plugins tools``` to see if your tool recognizes that the test belongs to it (and to check for naming/spelling errors). If it doesn't recognize it or it is misnamed, you'll need to edit the ```enumerate``` and ```can-run``` files for the tool to contain the correct test name.
