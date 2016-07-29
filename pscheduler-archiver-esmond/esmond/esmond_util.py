###
# Utilities for talking to esmond


import pscheduler
import requests
import socket

#disable SSL warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

log = pscheduler.Log(prefix="archiver-esmond", quiet=True)

DEFAULT_SUMMARIES = {
    "throughput": [
        {
            "summary-window":   86400,
            "event-type":   "throughput",
            "summary-type":   "average",
        },
    ],
    "packet-loss-rate": [
        {
            "summary-window":   300,
            "event-type":   "packet-loss-rate",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   3600,
            "event-type":   "packet-loss-rate",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   86400,
            "event-type":   "packet-loss-rate",
            "summary-type":   "aggregation",
        },
    ],
    "histogram-owdelay": [
        {
            "summary-window":   300,
            "event-type":   "histogram-owdelay",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   300,
            "event-type":   "histogram-owdelay",
            "summary-type":   "statistics",
        },
        {
            "summary-window":   3600,
            "event-type":   "histogram-owdelay",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   3600,
            "event-type":   "histogram-owdelay",
            "summary-type":   "statistics",
        },
        {
            "summary-window":   86400,
            "event-type":   "histogram-owdelay",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   86400,
            "event-type":   "histogram-owdelay",
            "summary-type":  "statistics",
        },
    ],
    "packet-loss-rate-bidir":[
        {
            "summary-window":   3600,
            "event-type":   "packet-loss-rate-bidir",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   86400,
            "event-type":   "packet-loss-rate-bidir",
            "summary-type":   "aggregation",
        },
    ],
    "histogram-rtt": [
        {
            "summary-window":   3600,
            "event-type":   "histogram-rtt",
            "summary-type":   "aggregation",
        },
    
        {
            "summary-window":   3600,
            "event-type":   "histogram-rtt",
            "summary-type":  "statistics",
        },
        {
            "summary-window":   86400,
            "event-type":   "histogram-rtt",
            "summary-type":   "aggregation",
        },
        {
            "summary-window":   86400,
            "event-type":   "histogram-rtt",
            "summary-type": "statistics",
        }
    ],
}

def iso8601_to_seconds(val):
    td = pscheduler.iso8601_as_timedelta(val)
    return (td.seconds + td.days * 86400)

def get_ips(addr):
    ip_v4 = None
    ip_v6 = None
    try:
        addrinfo = socket.getaddrinfo(addr, None)
        for ai in addrinfo:
            if ai[0] == socket.AF_INET:
                ip_v4 = ai[4][0]
            elif ai[0] == socket.AF_INET6:
                ip_v6 = ai[4][0]
    except:
        pass
    return ip_v4, ip_v6
    
def normalize_ip_versions(src, dest, ip_version=None):
    src_ip = None
    dest_ip = None
    src_ip_v4, src_ip_v6 = get_ips(src)
    dest_ip_v4, dest_ip_v6 = get_ips(dest)
    #prefer v6 if not specified
    if not ip_version or ip_version == 6:
       if src_ip_v6 and dest_ip_v6:
            src_ip = src_ip_v6
            dest_ip = dest_ip_v6
    if not src_ip or not dest_ip or ip_version == 4:
        if src_ip_v4 and dest_ip_v4:
            src_ip = src_ip_v4
            dest_ip = dest_ip_v4

    return src_ip, dest_ip

def build_event_type(event_type, summaries):
    et = { "event-type": event_type }
    if event_type in summaries:
        et["summaries"] = summaries[event_type]
    return et

def init_metadata(
                    test_spec=None,
                    lead_participant=None, 
                    tool_name=None,
                    event_types=[], 
                    summaries=None,
                    duration=None,
                    src_field="source", 
                    dst_field="dest", 
                    ipv_field="ip-version"
                ):
    #init
    metadata = { 'subject-type': 'point-to-point', 'event-types': [] }
    
    #determine source since its optional
    input_source = lead_participant
    if src_field in test_spec:
        input_source = test_spec[src_field]
        
    #get dest - should be required
    input_dest = test_spec[dst_field]
    
    #determine if we are forcing an ip-version
    ip_version = None
    if ipv_field in test_spec:
        ip_version = test_spec[ipv_field]
        
    #normalize ips
    src_ip, dest_ip = normalize_ip_versions(input_source, input_dest, ip_version=ip_version)
    
    #set fields
    metadata['source'] = src_ip
    metadata['destination'] = dest_ip
    metadata['input-source'] = input_source
    metadata['input-destination'] = input_dest
    metadata['tool-name'] = tool_name
    metadata['time-duration'] = duration
    #Make measurement-agent the lead participant, with same ip type as source
    src_ip, metadata['measurement-agent'] = normalize_ip_versions(src_ip, lead_participant)
    
    #Handle event types
    summary_map = DEFAULT_SUMMARIES
    if summaries:
        summary_map = summaries
    for et in event_types:
        metadata['event-types'].append(build_event_type(et, summary_map))
    
    return metadata

def add_metadata_fields(metadata={}, test_spec={}, field_map={}):
        for field in field_map:
            if field in test_spec:
                metadata[field_map[field]] = test_spec[field]

def init_datapoints(ts=None, test_result={}, field_map={}):
    data_point = { 'ts': ts, 'val': [] }
    for field in field_map:
        if field in test_result:
            data_point['val'].append({ 'event-type': field_map[field], 'val': test_result[field]})
    return [ data_point ]

def add_data_rate(data_point={}, event_type=None, test_result={}, numerator='', denominator=''):
    rate = 0
    if (numerator not in test_result) or (denominator not in test_result) or (test_result[numerator] is None) or (test_result[denominator] is None):
        return
    try:
        int(test_result[numerator])
        if int(test_result[denominator]) == 0: return 
    except:
        return
    data_point['val'].append({ 'event-type': event_type, 
                                'val': {'numerator': test_result[numerator], 'denominator': test_result[denominator]}})
                                    
                                        
class EsmondClient:
    url = ""
    verify_ssl = False
    headers = {}
    
    def __init__(self, url="http://127.0.0.1/esmond/perfsonar/archive", 
                        api_key=None, 
                        verify_ssl=False):
        self.url = url
        self.verify_ssl = verify_ssl
        self.headers = { 'Content-Type': 'application/json' }
        if api_key:
            self.headers['Authorization'] = "Token %s" % api_key
    
    def create_metadata(self, metadata):
        result = {}
        post_url = self.url
        if not post_url.endswith('/'):
            post_url += '/'
        log.debug("Posting metadata to %s: %s" % (post_url, metadata))
        r = requests.post(post_url, data=pscheduler.json_dump(metadata), headers=self.headers, verify=self.verify_ssl)
        if r.status_code != 200 and r.status_code != 201:
            try:
                return False, "%d: %s" % (r.status_code, pscheduler.json_load(r.text)['detail'])
            except:
                return False, "%d: %s" % (r.status_code, r.text)
        try:
            rjson = pscheduler.json_load(r.text)
            log.debug("rjson=%s" % rjson)
        except:
            return False, "Invalid JSON returned from server: %s" % r.text 
        
        return True, rjson
    
    def create_data(self, metadata_key, data_points):
        result = {}
        put_url = self.url
        if not put_url.endswith('/'):
            put_url += '/'
        put_url += ("%s/" % metadata_key)
        data = { 'data': data_points }
        log.debug("Putting data to %s: %s" % (put_url, data))
        r = requests.put(put_url, data=pscheduler.json_dump(data), headers=self.headers, verify=self.verify_ssl)
        if r.status_code== 409:
            #duplicate data
            log.debug("Attempted to add duplicate data point. Skipping")
        elif r.status_code != 200 and r.status_code != 201:
            try:
                return False, "%d: %s" % (r.status_code, pscheduler.json_load(r.text)['detail'])
            except:
                return False, "%d: %s" % (r.status_code, r.text)
        
        return True, ""
    