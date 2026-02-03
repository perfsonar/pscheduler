"""
Functions for determining the state of the system clock.  See
clock_state() below.
"""

import pscheduler
import datetime
import ntplib
import pytz
import shutil
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


_libc = cdll.LoadLibrary(find_library("c"))

def ntp_adjtime():

    timex = TimexStruct()
    p_timex = pointer(timex)

    _libc.ntp_adjtime(p_timex)

    return p_timex.contents


# ---------------------------

def _chronyc_status():
    '''
    Return time state as Chrony understands it or None if unable.
    '''

    status, stdout, stderr = pscheduler.run_program([ 'chronyc', 'tracking' ])

    if status == 2:
        # Chronyc wasn't found.
        return None

    if status == 1:
        # Ran but failed.
        if stdout is None or stdout.startswith('506 '):
            # No daemon to talk to
            return None

    parameters = stdout.split("\n")

    # TODO: Find a neater way to do this.
    reference_str = ""
    offset_str = ""
    for parameter in parameters:
        if "Reference" in parameter:
            reference_str = parameter
        if "Last offset" in parameter:
            offset_str = parameter

    result = {}
    try:
        offset = offset_str[offset_str.find(':'):]
        if offset != "":
            result["offset"] = float(offset[2:].split(" ")[0][1:])
        else:
            raise Exception("Offset not found")

        result["source"] = "chrony"

        reference = reference_str[reference_str.find('('):reference_str.find(')')]
        if reference != "":
            result["reference"] = reference[1:]
        else:
            raise Exception("Reference server not found")

    except Exception as ex:
        result["synchronized"] = False
        result["error"] = str(ex)

    return result


def _ntp_status():
    '''
    Return the time state as NTP understands it or None if unable.
    '''

    # See if ntpq is installed on the system.  This should keep
    # SELinux from raising its hackles over trying to access the
    # process table.

    if shutil.which('ntpq') is None:
         return None

    # NTPD might be running.  Try to query it.

    try:
        ntp = ntplib.NTPClient().request('localhost', timeout=2)
    except ntplib.NTPException:
        return None

    # There's a bug in ntplib < 0.4 where stratum 0 causes
    # stratum_to_text() to throw a TypeError.  See #1601.
    if ntp.stratum > 0:
        stratum_text = ntplib.stratum_to_text(ntp.stratum)
    else:
        stratum_text = "unspecified or invalid stratum"

    # Got some status.
    return {
        'offest': ntp.offset,
        'source': 'ntp',
        'reference': f'{stratum_text} from {ntplib.ref_id_to_text(ntp.ref_id)}'
    }


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

    # Grab the time now in case anyting below takes awhile.

    utc = datetime.datetime.utcnow()
    local_tz = tzlocal.get_localzone()
    time_here = pytz.utc.localize(utc).astimezone(local_tz)

    raw_offset = time_here.strftime("%z")
    if len(raw_offset):
        offset = raw_offset[:3] + ":" + raw_offset[-2:]
    else:
        offset = ""

    # See if the system thinks its clock is synchronized
    adjtime = ntp_adjtime()
    system_synchronized = adjtime.synchronized

    result = {
        "time": time_here.strftime("%Y-%m-%dT%H:%M:%S.%f") + offset,
        "synchronized": system_synchronized
    }


    # TODO: Can use result | xxx_result in Python >= 3.9
    chronyc_result = _chronyc_status()
    if chronyc_result is not None:
        return { **result, **chronyc_result }

    ntp_result = _ntp_status()
    if ntp_result is not None:
        return { **result, **ntp_result }

    # If nothing returned before this point, go with whatever we have.
    result['source'] = 'unknown'
    return result
