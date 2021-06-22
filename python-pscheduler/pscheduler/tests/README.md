# Tests and development

Documentation about running the `python-pscheduler` tests in a development environment.

## Setup and install

This presumes one already has an environment (virtual machine, etc) set up to run `pscheduler` and a python environment like a `virtualenv` that includes `pip`.

To set up some of the basic tools and to get all of the dependencies:

```
cd python-pscheduler/pscheduler
pip install -r dev-requirements.txt
```

This will:

* Install `pscheduler` in "editable" mode. That installs an egg link into the python installation that points to the checked out source code for "live" editing and testing.
* Install all of the third-party requirements for `pscheduler`.
* Install a couple of testing and development tools like `pylint` and `nose`.

## Running the tests

The test modules are standard issue python unit tests. They can be run however you please, but `dev-requirements.txt` installs the `nose` test runner.

To run the tests:

```
cd python-pscheduler/pscheduler
nosetests tests
```
The arg `tests` refers to the tests directory that lives in that directory. That command will run all of the unit tests.

To run the tests in a single module:

```
nosetests tests/sinumber_test.py
```

To run the tests in just one test class:

```
nosetests tests/sinumber_test.py:TestSinumber
```

To run a single test in a test class:

```
nosetests tests/sinumber_test.py:TestSinumber.test_si_range
```

The requirements file also installs `coverage`. It can be invoked from `nosetests` to create a coverage report by using the ` --with-coverage` flag.

### Gotchas

By default, `nosetests` will eat the output from any `print` statements. To disable this behavior either run like this:

```
nosetests --nocapture tests
```

Or create a `~/.noserc` file like this:

```
[nosetests]
verbosity=2
nocapture=true
```

There is a similar `--nologcapture` flag as well.