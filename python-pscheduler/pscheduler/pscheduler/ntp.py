#
# Originally from BWCTL2
#

# TODO: Works on Linux, but not OS X.

# TODO: Do this with ntplib, which is pure Python and talks to the
# local NTPD.

import datetime

from ctypes import *
from ctypes.util import find_library

"""
/* TODO: Can the structures here be #included? */

int ntp_adjtime(struct timex *);

#define STA_UNSYNC      0x0040  /* clock unsynchronized (rw) */

#define STA_NANO        0x2000  /* resolution (0 = us, 1 = ns) (ro) */

struct timex {
    int  modes;      /* Mode selector */
    long offset;     /* Time offset; nanoseconds, if STA_NANO
                        status flag is set, otherwise microseconds */
    long freq;       /* Frequency offset, in units of 2^-16 ppm
                        (parts per million, see NOTES below) */
    long maxerror;   /* Maximum error (microseconds) */
    long esterror;   /* Estimated error (microseconds) */
    int  status;     /* Clock command/status */
    long constant;   /* PLL (phase-locked loop) time constant */
    long precision;  /* Clock precision (microseconds, read-only) */
    long tolerance;  /* Clock frequency tolerance (ppm, read-only) */
    struct timeval time;
                     /* Current time (read-only, except for
                        ADJ_SETOFFSET); upon return, time.tv_usec
                        contains nanoseconds, if STA_NANO status
                        flag is set, otherwise microseconds */
    long tick;       /* Microseconds between clock ticks */
    long ppsfreq;    /* PPS (pulse per second) frequency (in units
                        of 2^-16 ppm--see NOTES, read-only) */
    long jitter;     /* PPS jitter (read-only); nanoseconds, if
                        STA_NANO status flag is set, otherwise
                        microseconds */
    int  shift;      /* PPS interval duration (seconds, read-only) */
    long stabil;     /* PPS stability (2^-16 ppm--see NOTES,
                        read-only) */
    long jitcnt;     /* PPS jitter limit exceeded (read-only) */
    long calcnt;     /* PPS calibration intervals (read-only) */
    long errcnt;     /* PPS calibration errors (read-only) */
    long stbcnt;     /* PPS stability limit exceeded (read-only) */
    int tai;         /* TAI offset, as set by previous ADJ_TAI
                        operation (seconds, read-only,
                        since Linux 2.6.26) */
    /* Further padding bytes to allow for future expansion */
};

struct timeval {
    time_t      tv_sec;     /* seconds */
    suseconds_t tv_usec;    /* microseconds */
};
"""

# TODO: Can these be derived form the above?
STA_NANO=0x2000
STA_UNSYNC=0x0040

class TimevalStruct(Structure):
    _fields_ = [
        ("tv_sec", c_long),
        ("tv_usec", c_long),
    ]

class TimexStruct(Structure):
    _fields_ = [
        ("modes", c_int),
        ("offset", c_long),
        ("freq", c_long),
        ("maxerror", c_long),
        ("esterror", c_long),
        ("status", c_int),
        ("constant", c_long),
        ("precision", c_long),
        ("tolerance", c_long),
        ("time", TimevalStruct),
        ("tick", c_long),
        ("ppsfreq", c_long),
        ("jitter", c_long),
        ("shift", c_int),
        ("stabil", c_long),
        ("jitcnt", c_long),
        ("calcnt", c_long),
        ("errcnt", c_long),
        ("stbcnt", c_long),
        ("tai", c_int),
    ]

    # Return true if the system is synchronized
    @property
    def is_synchronized(self):
        return (self.status & STA_UNSYNC) == 0

    # Return a timedelta with the offset in seconds
    # TODO: Check this on a NTP-synchronized host

    # TODO: This ain't working.

    @property
    def clock_offset(self):
        print self.offset
        return datetime.timedelta(
            seconds=5.0
            / float(10.0**9 if (self.status & STA_NANO) else 10.0**6)
            )

    @property
    def clock_precision(self):
        return datetime.timedelta(microseconds=self.precision)

    @property
    def error_est(self):
        return datetime.timedelta(seconds=self.esterror / 1000000.0)

    @property
    def error_max(self):
        return datetime.timedelta(seconds=self.maxerror / 1000000.0)


def ntp_adjtime():
    retval = None
    try:
        libc = cdll.LoadLibrary(find_library("c"))
        timex = TimexStruct()
        p_timex = pointer(timex)

        libc.ntp_adjtime(p_timex)

        retval = p_timex.contents
    except Exception as e:
        # TODO: Log something?
        pass

    return retval

if __name__ == "__main__":
    timex = ntp_adjtime()

    if timex is not None:
        print "Synchronized: ", timex.is_synchronized
        print "Offset: ", timex.clock_offset
        print "Precision: ", timex.clock_precision
        print "Est Error: ", timex.error_est
        print "Max Error: ", timex.error_max
    else:
        print "Not supported here."
