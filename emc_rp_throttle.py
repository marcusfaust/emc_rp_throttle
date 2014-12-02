__author__ = 'marcusfaust'

import requests
from requests.auth import HTTPBasicAuth


BASEURL = 'https://192.168.151.67/fapi/rest/4_0/settings/groups/all'
AUTH = HTTPBasicAuth('admin', 'admin')


def getThrottles():
    bandwidths = {}
    total = 0
    r = requests.get(BASEURL, verify=False, auth=AUTH)
    results = r.json()

    for group in results:
        print group['name']
        bandwidths[group['name']] = group['activeLinksSettings'][0]['linkPolicy']['protectionPolicy']['bandwidthLimit']
        total += group['activeLinksSettings'][0]['linkPolicy']['protectionPolicy']['bandwidthLimit']

    bandwidths['total'] = total
    return bandwidths



if __name__ == '__main__':
    bandwidths = getThrottles()


    print "hello"