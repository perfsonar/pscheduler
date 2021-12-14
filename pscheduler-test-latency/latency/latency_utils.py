###################################################################
# Contains classes and functions helpful in handling latency tests
###################################################################

import json
import sys
import os
import pscheduler
import math

'''
print float
'''
def format_float(label, value, units="", default="Not Reported"):
    prefix_length=22
    output = label + " ..."
    prefix_length -= len(output)
    for i in range(0, prefix_length):
        output += "."

    if value:
        output += " %.2f %s\n" % (value, units)
    else:
        output += " %s\n" % default
    
    return output


'''
Percentile: Used by histogram class to calculate percentiles using the NIST
algorithm (http://www.itl.nist.gov/div898/handbook/prc/section2/prc252.htm)
'''
class Percentile(object):
    
    def __init__(self, percentile, sample_size):
        self.value = None
        self.is_calculated = False
        self.percentile = percentile
        self.sample_size = sample_size
        self.n = (self.percentile/100.0)*(sample_size + 1)
        self.k = math.floor(self.n)
        self.d = self.n - self.k
        
        if percentile == 50:
            self.key = "median"
        else:
            self.key = "percentile-%d" % percentile
    
    def findvalue(self, count, hist_value):
        if self.value is not None:
            self.value += (self.d * (hist_value - self.value))
            self.is_calculated = True
        elif self.k == 0:
            self.value = hist_value
            self.is_calculated = True
        elif count >= self.sample_size and self.k >= self.sample_size:
            self.value = hist_value
            self.is_calculated = True
        elif (self.k + self.d) < count:
            self.value = hist_value
            self.is_calculated = True
        else:
            self.value = hist_value

'''
Histogram class used to calculate common histogram metrics
'''
class Histogram(object):
    
    def __init__(self, hist_dict):
        self.hist_dict = hist_dict
    
    def get_stats(self):
        #pass one: mode, mean and sample size
        stats = {}
        mean_num = 0
        sample_size = 0
        for k in self.hist_dict:
            #only can do statistics for histograms with numeric buckets
            try:
                float(k)
            except ValueError:
                return {}
            
            # update calculation values
            if 'mode' not in stats or self.hist_dict[k] > self.hist_dict[stats['mode'][0]]:
               stats['mode'] = [ k ]
            elif self.hist_dict[k] == self.hist_dict[stats['mode'][0]]:
                stats['mode'].append(k)
            mean_num += (float(k) * self.hist_dict[k])
            sample_size += self.hist_dict[k]
        if sample_size == 0:
            return {}
        stats['mean'] = (mean_num/(1.0*sample_size))
        
        #sort items. make sure sort as numbers not strings
        sorted_hist = sorted(iter(self.hist_dict.items()), key=lambda k: float(k[0]))
        
        #make mode floats.
        stats['mode'] = [float(x) for x in stats['mode']]
        #get min and max
        stats['minimum'] = float(sorted_hist[0][0])
        stats['maximum'] = float(sorted_hist[len(sorted_hist)-1][0])
        
        #pass two: get quantiles, variance, and std deviation
        stddev = 0
        quantiles = [25, 50, 75, 95]
        percentiles = [Percentile(q, sample_size) for q in quantiles]
        percentile = percentiles.pop(0)
        curr_count = 0
        for hist_item in sorted_hist:
            #stddev/variance
            stddev += (math.pow(float(hist_item[0]) - stats['mean'], 2)*hist_item[1])
            #quantiles
            curr_count += hist_item[1]
            while percentile is not None and curr_count >= percentile.k:
                percentile.findvalue(curr_count, float(hist_item[0]))
                #some percentiles require next item in list, so may have to wait until next iteration
                if percentile.is_calculated:
                    #calculated so add to dict
                    stats[percentile.key] = percentile.value
                else:
                    #unable to calculate this pass, so break loop
                    break
                
                #get next percentile
                if len(percentiles) > 0:
                    percentile = percentiles.pop(0)
                else:
                    percentile = None
                    
        #set standard deviation
        stats['variance'] = stddev/sample_size
        stats['standard-deviation'] = math.sqrt(stats['variance'])    
        return stats
