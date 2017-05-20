"""
Functions for determining the state of the system clock.  See
clock_state() below.
"""


import datetime
import ntplib
import pytz
import tzlocal

# The ntp_adjtime code is the only bit of BWCTL (actually BWCTL2) that
# survived into pScheduler.

from ctypes import *
from ctypes.util import find_library

"""
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

STA_NANO = 0x2000
STA_UNSYNC = 0x0040


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

    @property
    def synchronized(self):
        return (self.status & STA_UNSYNC) == 0


def ntp_adjtime():
    retval = None
    try:
        libc = cdll.LoadLibrary(find_library("c"))
        timex = TimexStruct()
        p_timex = pointer(timex)

        libc.ntp_adjtime(p_timex)

        retval = p_timex.contents
    except Exception as e:
        return None

    return retval


# ---------------------------


def clock_state():
    """
    Determine the state of the system clock and return a hash of
    information conforming to the definition of a SystemClockStatus
    object as described in the JSON dictionary.

    time - Current system time as an ISO 8601 string

    synchronized - Whether or not the clock is synchronized to an
    outside source.

    source - The source of synchronization.  Currently, the only valid
    value is "ntp."  Not provided if not synchronized.

    reference - A human-readable string describing the source.  Not
    provided if not synchronized.

    offset - A float indicating the estimated clock offset.  Not
    provided if not synchronized.

    error -

    """

    adjtime = ntp_adjtime()
    system_synchronized = adjtime.synchronized

    # Format the local time with offset as ISO 8601.  Python's
    # strftime() only does "-0400" format; we need "-04:00".

    utc = datetime.datetime.utcnow()
    local_tz = tzlocal.get_localzone()
    time_here = pytz.utc.localize(utc).astimezone(local_tz)

    raw_offset = time_here.strftime("%z")
    if len(raw_offset):
        offset = raw_offset[:3] + ":" + raw_offset[-2:]
    else:
        offset = ""

    result = {
        "time": time_here.strftime("%Y-%m-%dT%H:%M:%S.%f") + offset,
        "synchronized": system_synchronized
    }

    if system_synchronized:

        # Assume NTP for the time being

        try:
            ntp = ntplib.NTPClient().request("127.0.0.1")
            result["offset"] = ntp.offset
            result["source"] = "ntp"
            result["reference"] = "%s from %s" % (
                ntplib.stratum_to_text(ntp.stratum),
                ntplib.ref_id_to_text(ntp.ref_id)
            )
        except Exception as ex:
            result["synchronized"] = False
            result["error"] = str(ex)

    return result


if __name__ == "__main__":
    import pscheduler
    print pscheduler.json_dump(clock_state(), pretty=True)
