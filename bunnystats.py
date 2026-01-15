from collections import Counter
from urllib.parse import urlencode

import csv
import requests

def get_total_transfer_bytes(pull_zone_id, from_date, to_date_incl, api_key):
    url = 'https://api.bunny.net/statistics?' + urlencode({
        'dateFrom': from_date.isoformat(),
        'dateTo': to_date_incl.isoformat(),
        'pullZone': pull_zone_id,
        'serverZoneId': '-1',
        'loadErrors': 'false',
        'hourly': 'false'
    })
    headers = {
        "accept": "application/json",
        "AccessKey": api_key
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()['TotalBandwidthUsed']

def get_transfer_bytes_per_url(pull_zone_id, date, auth_token):
    # N.B. This significantly under-reports traffic because Bunny's logging API
    # does not return data for all requests.
    date_str = date.strftime('%m-%d-%y')
    url = f'https://logging.bunnycdn.com/{date_str}/{pull_zone_id}.log'
    resp = requests.get(url, headers={'Authorization': auth_token})
    if resp.status_code == 404:
        # This happens when there is no data for the given day. For example,
        # when the pull zone did not yet exist.
        return Counter()
    resp.raise_for_status()
    result = Counter()
    for row in csv.reader(resp.text.splitlines(), delimiter='|'):
        result[row[7]] += int(row[3])
    return result

def get_auth_token(email, password):
    resp = requests.post('https://api.bunny.net/auth/jwt', {
        'Email': email,
        'Password': password,
        'Utm': {}
    })
    resp.raise_for_status()
    return resp.json()['Token']
