import pscheduler
import json
import os

logger = pscheduler.Log(prefix='tool-perftest', quiet=True)


def parse_output(file_path=None, duration=0):
    result = {
        'succeeded': True,
    }
    summary = {
        'omitted': False,
        'start': 0,
        'end': duration,
        'stream-id': 0,
    }

    if file_path is None or not os.path.exists(file_path):
        return {
            'succeeded': False,
            'error': f'perftest result parsing failed: no output file, path provided: {"" if file_path is None else file_path}'
        }
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            result['mtu'] = data['test_info']['Mtu']
            summary['sent'] = data['results']['n_iterations']
            summary['throughput-bits'] = int(data['results']['BW_average'] * 1e9)
            summary['throughput-bytes'] = int(data['results']['BW_average'] * 1e9 / 8)
            summary['receiver-throughput-bits'] = 0
            result['summary'] = {
                'summary': summary,
                'streams': [summary]
            }
            result['intervals'] = [{
                'summary': summary,
                'streams': [summary]
            }]
    except Exception as e:
        return {
            'succeeded': False,
            'error': f'perftest result parsing failed: {e}'
        }
    return result
