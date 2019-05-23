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

#### Enable Debugging logging at /var/log/pscheduler/pscheduler.log
```
pscheduler debug on runner
```
#### Sometimes viewing a variable is useful in debugging. Use the following to write a variable to a file and save at /tmp
with open('/tmp/run_log.txt', 'wb') as f:
  f.write('LOGGING output of variable STDERR')
  f.write(str(STDERR))
