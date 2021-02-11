# Limit Processor Development Notes

## Thread Safety

The core of the limit processor is thread-safe.  Some of the
identifiers (namely `ip-cidr-list-url`) maintain internal state that
is updated from outside sources.  These identifiers must have a lock
around changes to that state to prevent other treads from trying to
update that state while one is in progress.
