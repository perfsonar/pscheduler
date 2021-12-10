"""
Drop-in replacement for select() based on poll()
"""

import select


# EOF/HUP aren't treated the same way across all platforms or even all
# types of file on the same platform (Linux, some BSDs), so include it
# in read conditions.
# See https://www.greenend.org.uk/rjk/tech/poll.html
POLL_READ = select.POLLIN | select.POLLPRI | select.POLLHUP
POLL_WRITE = select.POLLOUT
POLL_EXCEPT = select.POLLERR | select.POLLNVAL


def polled_select(reads, writes, excepts, timeout=None):
    """
    select(2) work-alike based on poll(2).  See Python documentation.

    # PORT: poll is not supported on all platforms.
    """

    registered = {}

    def register(fdlist, flags):
        for orig_fd in fdlist:
            # Poll returns integers, so convert to that.
            if hasattr(orig_fd, 'fileno'):
                fd = orig_fd.fileno()
            else:
                fd = orig_fd
            try:
                registered[fd]["flags"] |= flags
            except KeyError:
                registered[fd] = {
                    "fd": orig_fd,
                    "flags": flags
                }

    register(reads, POLL_READ)
    register(writes, POLL_WRITE)
    register(excepts, POLL_EXCEPT)

    poller = select.poll()
    for reg in registered:
        poller.register(reg, registered[reg]["flags"])


    fds = poller.poll(timeout * 1000.0 if timeout is not None else None)

    read = []
    wrote = []
    excepted = []

    for fd, flags in fds:
        reg_flags = registered[fd]["flags"]
        try:
            if flags & POLL_READ and reg_flags & POLL_READ:
                read.append(registered[fd]["fd"])
            if flags & POLL_WRITE and reg_flags & POLL_WRITE:
                wrote.append(registered[fd]["fd"])
            if flags & POLL_EXCEPT:  # These get logged no matter what.
                excepted.append(registered[fd]["fd"])
        except KeyError:
            pass

    return read, wrote, excepted
