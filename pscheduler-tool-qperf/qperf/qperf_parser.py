import re
import pscheduler

logger = pscheduler.Log(quiet=True)

def to_bits(value_str):
    unit_map = {
        'Kb': 1e3,
        'Mb': 1e6,
        'Gb': 1e9,
        'Tb': 1e12,
        'KB': 8e3,
        'MB': 8e6,
        'GB': 8e9,
        'TB': 8e12,
        'B': 8,
    }

    pattern = re.compile(r'([\d.]+)\s*(K|M|G|T)?(b|B)(/sec)?')
    match = pattern.search(value_str.strip())

    if not match:
        raise ValueError(f'Cannot parse bits from "{value_str}"')

    value, prefix, btype, _ = match.groups()
    unit = (prefix or '') + btype

    if unit not in unit_map:
        raise ValueError(f'Unknown unit "{unit}" in "{value_str}"')

    bits = int(float(value) * unit_map[unit])

    return bits


def to_count(value_str):
    multipliers = {
        'thousand': 1e3,
        'million': 1e6,
        'billion': 1e9,
        'trillion': 1e12
    }

    value_str = value_str.strip().replace(',', '')

    pattern = re.compile(r'([\d.]+)\s*(thousand|million|billion|trillion)?', re.IGNORECASE)
    match = pattern.search(value_str)

    if not match:
        raise ValueError(f'Cannot parse count from "{value_str}"')

    value, word = match.groups()
    multiplier = multipliers.get(word.lower(), 1) if word else 1
    return int(float(value) * multiplier)


def translate_line(key, value):
    if key == 'bw':
        return {
            'throughput-bits': to_bits(value),
            'throughput-bytes': to_bits(value) / 8,
            'receiver-throughput-bits': to_bits(value)
        }
    if key == 'send_bw':
        return {
            'throughput-bits': to_bits(value),
            'throughput-bytes': to_bits(value) / 8,
        }
    if key == 'recv_bw':
        return {
            'receiver-throughput-bits': to_bits(value)
        }
    if key == 'loc_send_msgs':
        return {
            'sent': to_count(value)
        }
    if key == 'rem_recv_msgs':
        return {
            'received': to_count(value)
        }
    return {}


def parse_output(lines, duration=0):
    results = {
        'succeeded': True,
    }
    summary = {
        'omitted': False,
        'start': 0,
        'end': duration,
        'stream-id': 0,
    }
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            summary.update(translate_line(key.strip(), value.strip()))
    if summary.get('sent') and summary.get('received'):
        summary['lost'] = summary['sent'] - summary['received']
    _ = summary.pop('received', None)

    results['summary'] = {
        'summary': summary,
        'streams': [summary]
    }
    results['intervals'] = [{
        'summary': summary,
        'streams': [summary]
    }]
    return results
